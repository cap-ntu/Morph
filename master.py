import os
import md5
import time
import Queue
import socket
import config
import struct
import threading
import subprocess
import SocketServer
from common import *
from random import Random
from SocketServer import TCPServer
from SocketServer import ThreadingMixIn
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

#used to store the task information
tasks_queue = {}

#the lock used to access the tasks_queue
lock = threading.Lock()

#the original videos which needs to be split into blocks
split_queue = Queue.Queue(maxsize = 100)

#the video blocks after slicing
block_queue = Queue.Queue(maxsize = 1000)

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


def add_trans_task(file_path, bitrate, width, height):

    key_val             = gen_key()
    new_task            = task()

    new_task.task_id    = key_val
    new_task.file_path  = file_path
    new_task.bitrate    = bitrate
    new_task.width      = width
    new_task.height     = height
    new_task.num        = -1

    #put the transcoding task into the queue
    task_stat = task_status()
    task_stat.start_time = time.time()
    task_stat.progress   = 1
    lock.acquire()
    tasks_queue[key_val] = task_stat
    lock.release()

    split_queue.put_nowait(new_task)
    print 'put the task into the splitting queue'
    return key_val


def query_result(task_id):
    pass


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
        seg_dur         = 60 * 10
        file_path       = task.file_path
        base_name       = os.path.basename(file_path)
        (prefix,suffix) = os.path.splitext(base_name)
        work_path       = config.master_path
        list_file_path  = os.path.join(work_path, task.task_id + ".list")
        segm_file_path  = os.path.join(work_path, task.task_id + "_%03d_" + suffix)

        cmd = "ffmpeg -i " + file_path + " -f segment -segment_time " + str(seg_dur) + \
                " -c copy -map 0 -segment_list " + list_file_path + "  " + segm_file_path
        print cmd

        #os.system(cmd)
        print 'start to split the video into segments'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        ret = p.returncode
        print 'the return code is:', ret
        if ret != 0:
            return

        f = open(list_file_path)
        lines = f.readlines()
        f.close()

        index = 0
        for line in lines:
            block_info = block()
            line = line.strip('\n')

            block_info.task_id       = task.task_id
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

            block_queue.put(block_info)
            index = index + 1
            #put the video blocks into the splitting queue

        lock.acquire()
        task_stat = tasks_queue[task.task_id]
        task_stat.block_num = len(lines)
        task_stat.progress  = 2
        lock.release()

    def run(self):
        while True:
            task = split_queue.get(True)
            print('Worker %s got task %s for splitting' % (self.index, task.task_id))
            self.split_video(task)


#get the current number of blocks in queue
def get_blk_num():
    return block_queue.qsize()

#responsible for sending data blocks to the workers
class send_data(SocketServer.BaseRequestHandler):

    def handle(self):
        print 'get the sending data request'
        try:
            block  = block_queue.get_nowait()
            f      = open(block.file_path, 'rb')
            data   = f.read()
            f.close()

            pack    = pack_block_info(block)
            data_block = pack + data
            print 'data_block length:', len(data_block)

            sum = 0
            while True:
                cnt = self.request.send(data_block[sum: sum + 1024*400])
                sum = cnt + sum
                if cnt == 0:
                    print 'the number of bytes sent:', sum
                    self.request.shutdown(socket.SHUT_WR)
                    break

            ret_msg = self.request.recv(10)
            print 'the return msg is:', ret_msg
            self.request.close()

        except Exception, ex:
            self.request.close()
            print ex


class send_data_thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print 'start the sending data thread'
        server = ThreadedTCPServer((master_ip, master_snd_port), send_data)
        server.serve_forever()


class recv_data(SocketServer.BaseRequestHandler):

    def handle(self):
        print 'get the receiving data request'
        flag        = 0
        data_block  = ''
        success     = 0
        block_info  = block()
        work_path   = config.master_path
        print 'begin to receive data from worker'

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
                    block_info.status)   = struct.unpack(block_format, data_block[0:struct.calcsize(block_format)])

                if not data:
                    break

            if block_info.size == len(data_block) - struct.calcsize(block_format):
                print 'received data: length okay'
            else:
                print block_info.size
                print len(data_block) - struct.calcsize(block_format)
                print 'received data: length error'
                return None

            key = md5.new()
            key.update(data_block[struct.calcsize(block_format):])
            val = key.hexdigest()

            if block_info.md5_val == val:
                print 'received data: md5 check okay'
                self.request.sendall('okay')

                path_len    = block_info.path_len
                base_name   = os.path.basename(block_info.file_path[0:path_len])
                new_path    = os.path.join(work_path, base_name)

                block_info.file_path = new_path
                block_info.path_len  = len(new_path)

                #new_task = task_status()
                #new_task.block  = block_info

                task_id     = block_info.task_id
                block_id    = block_info.block_no

                lock.acquire()
                task_stat           = tasks_queue[task_id]
                task_stat.fin_num   += 1
                task_stat.block[block_id] = block_info
                lock.release()

                f = open(new_path, 'wb')
                f.write(data_block[struct.calcsize(block_format):])
                f.close()
                sucess = 1
            else:
                print 'received data: md5 check fail'
                self.request.sendall('fail')
                sucess = 0

        except Exception, ex:
            print ex
            self.request.sendall('fail')
            sucess = 0
        finally:
            self.request.close()
            if sucess == 1:
                return block_info
            else:
                return None


class recv_data_thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print 'start the receiving data thread'
        server = ThreadedTCPServer((master_ip, master_rev_port), recv_data)
        server.serve_forever()


class task_status_checker(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def concat_block(self, task):
        print 'concatenate the blocks:'
        total_no    = task.block_num
        file_path   = task.block[0].file_path

        dir_name    = os.path.dirname(file_path)
        base_name   = os.path.basename(file_path)
        (pre, suf)  = os.path.splitext(base_name)

        task_id     = task.block[0].task_id
        list_file   = os.path.join(dir_name, task_id + '.list')
        new_file    = os.path.join(dir_name, task_id + suf)

        f = open(list_file, 'w')
        for i in range(0, total_no):
            line = 'file ' + '\'' + task.block[i].file_path + '\'' + '\n'
            print line
            f.write(line)
        f.close()

        cmd = 'ffmpeg -f concat -i ' + list_file + ' -c copy ' + new_file
        #os.system(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        ret = p.returncode

    def run(self):
        while True:
            #print 'current number of ongoing tasks:', len(tasks_queue)
            #print 'current number of blocks in queue:', get_blk_num()

            lock.acquire()
            task_stat = None
            for task_id in tasks_queue.keys():
                task_stat   = tasks_queue[task_id]
                fin_blk_no  = task_stat.fin_num

                if fin_blk_no == task_stat.block_num:
                    print 'job finished'
                    tasks_queue.pop(task_id)
                    self.concat_block(task_stat)

            lock.release()
            time.sleep(2)


if __name__ == '__main__':

    #start the rpc thread to handle the request
    server = master_rpc_server((master_ip, master_rpc_port))
    server.register_function(add_trans_task, "add_trans_task")
    server.register_function(query_result, "query_result")
    server.register_function(get_blk_num,  "get_blk_num")

    #create the thread for splitting video files
    for i in range(3):
        t = split_thread(i)
        t.start()

    #create the thread for sending data blocks to the worker
    t = send_data_thread()
    t.start()

    t = recv_data_thread()
    t.start()

    t = task_status_checker()
    t.start()

    server.serve_forever()



