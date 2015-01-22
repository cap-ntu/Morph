import os
import sys
import md5
import time
import pycurl
import pickle
import Queue
import logging
import urlparse
import socket
import config
import struct
import threading
import subprocess
import SocketServer
from common import *
from random import Random
from Queue import PriorityQueue
from SocketServer import TCPServer
from SocketServer import ThreadingMixIn
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

#the handler of the log module
logger = None

#used to store the task information
tasks_queue = {}

#the lock used to access the tasks_queue
lock = threading.Lock()

#the original videos which need to be split into blocks
split_queue = PriorityQueue(100)

#the video blocks after slicing
block_queue = PriorityQueue(5000)

#the ip and port information of the master server
master_ip       = config.master_ip
master_rev_port = int(config.master_rev_port)
master_snd_port = int(config.master_snd_port)
master_rpc_port = int(config.master_rpc_port)


class master_rpc_server(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass

# This function is used to generate a random string as the key of the task
def gen_key(randomlength = 8):
    str     = ''
    chars   = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length  = len(chars) - 1
    random  = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

def download_video(url, task_id):
    file_name = url.split('/')[-1]
    name, ext = os.path.splitext(file_name)
    file_name = task_id + ext
    file_name = os.path.join(config.master_path, file_name)

    try:
        with open(file_name, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, f)
            c.perform()
            c.close()
    except:
        file_name = ''
    finally:
        return file_name


def put_trans_task(URI, bitrate, width, height, priority, task_id):

    #key_val            = gen_key()
    key_val             = task_id
    new_task            = task()
    file_path           = URI

    log_msg = 'the generated key: %s' % key_val
    logger.debug(log_msg)

    new_task.task_id    = key_val
    new_task.file_path  = file_path
    new_task.bitrate    = bitrate
    new_task.width      = width
    new_task.height     = height
    new_task.num        = -1
    new_task.priority   = priority

    #put the transcoding task into the queue
    task_stat = task_status()
    task_stat.start_time = time.time()
    task_stat.progress   = 1

    lock.acquire()
    try:
        tasks_queue[key_val] = task_stat
    finally:
        lock.release()

    split_queue.put_nowait((new_task.priority, 1, new_task))
    log_msg = 'put the task, task id: %s, priority: %s' % \
            (new_task.task_id, new_task.priority)
    logger.info(log_msg)
    print dump_msg(TASKID = task_id, PROGRESS = 10)
    return key_val


def get_progress(task_id):
    work_path = config.master_path
    f_name = os.path.join(work_path, task_id + '.pkl')
    if os.path.isfile(f_name) == True:
        pkl_file = open(f_name, 'rb')
        task_status = pickle.load(pkl_file)
        pkl_file.close()
        return task_status.progress
    else:
        if task_id in tasks_queue.keys():
            lock.acquire()
            try:
                task_stat = tasks_queue[task_id]
            finally:
                lock.release()

            ret = task_stat.progress
            return ret
        else:
            return -100


class split_thread(threading.Thread):

    def __init__(self, index):
        threading.Thread.__init__(self)
        self.index = index

    '''
    This function is used to split the video into segments:
    The video segment command should be:
    ffmpeg -i china.mp4 -f segment -segment_time 10 -c copy -map 0 \
            -segment_list china.list china%03d.mp4
    '''
    def split_video(self, task):

        file_path = ''

        if task.file_path[0] != 'L' and task.file_path[0] != 'U':
            return -1

        if task.file_path[0] == 'L':
            file_path = task.file_path[1:]
        elif task.file_path[0] == 'U':
            url  = task.file_path[1:]
            file_path = download_video(url, task.task_id)
            if file_path == '':
                return -1

        task.file_path  = file_path

        seg_dur         = config.segment_duration
        base_name       = os.path.basename(file_path)
        (prefix,suffix) = os.path.splitext(base_name)
        work_path       = config.master_path
        list_file_path  = os.path.join(work_path, task.task_id + ".list")
        segm_file_path  = os.path.join(work_path, task.task_id + "_%03d_" + suffix)

        cmd = "ffmpeg -i " + file_path + " -f segment -segment_time " + str(seg_dur) + \
                " -c copy -map 0 -segment_list " + list_file_path + "  " + segm_file_path
        logger.debug('%s: %s', task.task_id, cmd)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        ret = p.returncode
        logger.info('the return code is: %s', ret)

        if ret != 0:
            lock.acquire()
            try:
                task_stat = tasks_queue[task.task_id]
                task_stat.progress = -1
            finally:
                lock.release()
            return

        f = open(list_file_path)
        lines = f.readlines()
        f.close()

        index = 0
        for line in lines:
            block_info = block()
            line = line.strip('\n')

            block_info.task_id       = task.task_id
            block_info.priority      = task.priority
            block_info.file_path     = os.path.join(work_path, line)
            block_info.path_len      = len(block_info.file_path)
            block_info.block_no      = index
            block_info.total_no      = len(lines)
            block_info.bitrate       = task.bitrate
            block_info.width         = task.width
            block_info.height        = task.height
            block_info.size          = os.path.getsize(block_info.file_path)

            f    = open(block_info.file_path, 'rb')
            data = f.read()
            f.close()

            key = md5.new()
            key.update(data)
            block_info.md5_val = key.hexdigest()

            block_queue.put((block_info.priority, 1, block_info))
            index = index + 1
            #put the video blocks into the splitting queue

        lock.acquire()
        try:
            task_stat = tasks_queue[task.task_id]
            task_stat.block_num = len(lines)
            task_stat.progress  = 2
            print dump_msg(TASKID = task.task_id, PROGRESS = 20)
        finally:
            lock.release()

    def run(self):
        logger.debug('start worker for splitting: %s', self.index)
        while True:
            _, _, task = split_queue.get(True)
            log_msg = '%s: Worker %s got task for splitting' % (task.task_id, self.index)
            logger.debug(log_msg)
            self.split_video(task)


#get the current number of blocks in queue
def get_blk_num():
    return block_queue.qsize()

#responsible for sending data blocks to the workers
class send_data(SocketServer.BaseRequestHandler):

    def handle(self):

        logger.debug('start to send data to the woker')
        p_1     = None
        p_2     = None
        block   = None
        try:
            p_1, p_2, block  = block_queue.get_nowait()
            f      = open(block.file_path, 'rb')
            data   = f.read()
            f.close()

            pack    = pack_block_info(block)
            data_block = pack + data
            logger.debug('data block length: %s', len(data_block))

            sum = 0
            while True:
                cnt = self.request.send(data_block[sum: sum + 1024*400])
                sum = cnt + sum
                if cnt == 0:
                    logger.debug('the number of bytes sent: %s', sum)
                    self.request.shutdown(socket.SHUT_WR)
                    break

            ret_msg = self.request.recv(10)
            self.request.close()

            logger.debug('the return msg is: %s', ret_msg)

            if ret_msg == 'okay':
                logger.debug('send data to the worker successfully')
            else:
                block_queue.put((p_1, p_2, block))
                logger.error('fail to send the data to the worker, put back the task')

        except Queue.Empty:
            self.request.close()
            logger.error('no task in Queue')
        except Exception, ex:
            self.request.close()
            if block != None:
                block_queue.put((p_1, p_2, block))
            logger.error('fail to send data')


class send_data_thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        logger.debug('start the sending data thread')
        server = ThreadedTCPServer((master_ip, master_snd_port), send_data)
        server.serve_forever()


class recv_data(SocketServer.BaseRequestHandler):

    def write_file(self, block_info, data_block):
        cur = 0
        num = 0
        fs  = [0, 0, 0, 0, 0, 0]
        (num, fs[0], fs[1], fs[2], fs[3], fs[4], fs[5]) = \
                struct.unpack(format_length, data_block[0:struct.calcsize(format_length)])
        cur = cur + struct.calcsize(format_length)

        base_name   = os.path.basename(block_info.file_path)
        base_name   = base_name.replace('_package', '')
        (prefix,suffix) = os.path.splitext(base_name)

        width   = block_info.width.replace(' ', '').split('%')
        width   = filter(lambda a: a != '', width)
        height  = block_info.height.replace(' ', '').split('%')
        height  = filter(lambda a: a != '', height)

        for i in range(len(width)):
            resolution = width[i] + 'x' + height[i]
            new_path   = os.path.join(config.master_path, prefix + resolution + suffix)
            f = open(new_path, 'wb')
            f.write(data_block[cur:cur + fs[i]])
            f.close()
            cur = cur + fs[i]

    def handle(self):

        flag        = 0
        data_block  = ''
        success     = -1
        block_info  = block()
        work_path   = config.master_path
        logger.debug('begin to receive data from worker')

        try:
            while True:
                data = self.request.recv(1024*400)
                data_block = data_block + data
                if flag == 0 and len(data_block) >= struct.calcsize(block_format):
                    flag = 1
                    (block_info.task_id,  \
                    block_info.path_len,  \
                    block_info.file_path, \
                    block_info.block_no,  \
                    block_info.total_no,  \
                    block_info.bitrate,   \
                    block_info.width,     \
                    block_info.height,    \
                    block_info.size,      \
                    block_info.md5_val,   \
                    block_info.status,
                    block_info.priority)   = struct.unpack(block_format, data_block[0:struct.calcsize(block_format)])

                if not data:
                    break

            if flag == 0:
                success = 0
                logger.debug('cannot decode the header')
                return

            if block_info.size == len(data_block) - struct.calcsize(block_format):
                logger.debug('received data: length okay')
            else:
                logger.debug('received data: length error')
                success = 0
                return

            key = md5.new()
            key.update(data_block[struct.calcsize(block_format):])
            val = key.hexdigest()

            if block_info.md5_val == val:
                logger.debug('received data: md5 check okay')
                self.request.sendall('okay')
                self.request.shutdown(socket.SHUT_WR)

                path_len    = block_info.path_len
                base_name   = os.path.basename(block_info.file_path[0:path_len])
                new_path    = os.path.join(work_path, base_name)

                block_info.file_path = new_path
                block_info.path_len  = len(new_path)

                task_id     = block_info.task_id
                block_id    = block_info.block_no

                #check whehter the transcoding task is successful
                lock.acquire()
                try:
                    task_stat = tasks_queue[task_id]
                    if block_info.status == 0 and task_stat.progress > 0:
                        if block_id in task_stat.block.keys():
                            task_stat.block[block_id] = block_info
                        else:
                            task_stat.fin_num   += 1
                            task_stat.block[block_id] = block_info
                    else:
                        success = 0
                        task_stat.progress = -2
                finally:
                    lock.release()

                if success == 0:
                    return

                self.write_file(block_info, data_block[struct.calcsize(block_format):])
                success = 1
            else:
                logger.error('received data: md5 check fail')
                self.request.sendall('fail')
                self.request.shutdown(socket.SHUT_WR)
                success = 0

        except Exception, ex:
            #print ex
            self.request.sendall('fail')
            success = 0
        finally:
            self.request.close()
            if success == 1:
                return block_info
            else:
                return None


class recv_data_thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        logger.debug('start the receiving data thread')
        server = ThreadedTCPServer((master_ip, master_rev_port), recv_data)
        server.serve_forever()


class task_status_checker(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def write_pkl(self, task_id, task):
        work_path = config.master_path
        f_name = os.path.join(work_path, task_id + '.pkl')
        output = open(f_name, 'wb')
        pickle.dump(task, output)
        output.close()

    def concat_block(self, task):
        logger.debug('concatenate the blocks')
        total_no    = task.block_num

        width   = task.block[0].width.replace(' ', '').split('%')
        width   = filter(lambda a: a != '', width)
        height  = task.block[0].height.replace(' ', '').split('%')
        height  = filter(lambda a: a != '', height)

        suf     = ''
        task_id = task.block[0].task_id

        for i in range(len(width)):
            resolution = width[i] + 'x' + height[i]
            list_path  = os.path.join(config.master_path, \
                    task_id + '_' + resolution + '.list')
            f = open(list_path, 'w')
            for i in range(0, total_no):
                path        = task.block[i].file_path
                dir_name    = os.path.dirname(path)
                base_name   = os.path.basename(path)
                base_name   = base_name.replace('_package', '')
                (pre, suf)  = os.path.splitext(base_name)
                file_name   = os.path.join(dir_name, \
                                 pre + resolution + suf)
                line = 'file ' + '\'' + file_name + '\'' + '\n'
                f.write(line)
            f.close()

            new_file = os.path.join(config.master_path, \
                    task_id + '_' + resolution + suf)
            cmd = 'ffmpeg -f concat -i ' + list_path + ' -c copy ' + new_file
            logger.debug('%s', cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = p.communicate()
            ret = p.returncode
            logger.info('return code: %s', ret)
            if ret != 0:
                return ret

        return 0

    def run(self):
        while True:
            #print 'current number of ongoing tasks:', len(tasks_queue)
            #print 'current number of blocks in queue:', get_blk_num()

            lock.acquire()
            try:
                task_stat = None
                for task_id in tasks_queue.keys():
                    task_stat   = tasks_queue[task_id]
                    fin_blk_no  = task_stat.fin_num

                    #video concatenation
                    if fin_blk_no == task_stat.block_num and task_stat.progress == 2:
                        logger.debug('job finished')
                        tasks_queue.pop(task_id)
                        ret = self.concat_block(task_stat)
                        if ret == 0:
                            task_stat.progress = 3
                            print dump_msg(TASKID = task_id, PROGRESS = 100)
                            cur_time = time.time()
                            dur_time = cur_time - task_stat.start_time
                            logger.info('transcoding duration: %s', dur_time)
                        else:
                            task_stat.progress = -3
                        self.write_pkl(task_id, task_stat)
                        continue

                    #cancel a task
                    if task_stat.progress < 0:
                        tasks_queue.pop(task_id)
                        self.write_pkl(task_id, task_stat)
                        continue

                    #others, i.e., time out
            finally:
                lock.release()

            time.sleep(2)

class RequestHandler(SimpleXMLRPCRequestHandler):
    def log_message(self, format, *args):
        pass


if __name__ == '__main__':

    logger = init_log_module("master", master_ip, logging.DEBUG)
    logger.debug('start the master server')

    work_path = config.master_path
    if os.path.exists(work_path) == False:
        logger.critical('work path does not exist:%s', work_path)
        sys.exit()

    #start the rpc thread to handle the request
    server = master_rpc_server((master_ip, master_rpc_port), requestHandler = RequestHandler)
    server.register_function(put_trans_task, "put_trans_task")
    server.register_function(get_progress, "get_progress")
    server.register_function(get_blk_num,  "get_blk_num")

    #create the thread for splitting video files
    for i in range(config.split_thread_num):
        t = split_thread(i)
        t.start()

    #create the thread for sending data blocks to the worker
    t = send_data_thread()
    t.start()

    #create the thread for receiving the data blocks from the workers
    t = recv_data_thread()
    t.start()

    #create the thread for checking tasks
    t = task_status_checker()
    t.start()

    #never stop
    server.serve_forever()



