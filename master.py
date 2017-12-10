'''
Author: Guanyu Gao
Email: guanyugao@gmail.com
Description: The main file for the master, responsible for task
scheduling, block dispatching, video splitting and concentration.
'''

import config
import numpy as np
import os, sys, md5
import time, pycurl
import pickle, Queue
import logging, urlparse, socket
import struct, threading
import subprocess, SocketServer
from common import *
from sys_info import *
from Queue import PriorityQueue
from SocketServer import TCPServer
from SocketServer import ThreadingMixIn
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

sys.path.append("algorithms")
from scheduling import *

#the handler of the log and database module
logger = None

#store the task information
task_status = {}

#the queue used for task scheduling
sched_queue = []

#task preprocessing, e.g., time estimation, download.
preproc_queue = Queue.Queue(100)

#the video blocks waitting for distributing
disb_queue = Queue.Queue(5000)

#the blocks that have been dispatched, not been finished
ongoing_blocks = []

#the ip and port information of the master server
master_ip       = config.master_ip
master_rev_port = int(config.master_rev_port)
master_snd_port = int(config.master_snd_port)
master_rpc_port = int(config.master_rpc_port)


class master_rpc_server(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass

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

'''
submit a new task, RPC interface for calling
'''
def put_trans_task(URI, bitrate, width, height, priority, task_id = None):

    if task_id == None:
        task_id = gen_key()

    if task_id in task_status.keys():
        return task_id

    log_msg = 'new task: %s' % task_id
    logger.debug(log_msg)

    #insert the task information into database
    db_insert_task_info(task_id, priority)

    width  = (width + '%').ljust(30)
    height = (height + '%').ljust(30)

    new_task            = task()
    new_task.task_id    = task_id
    new_task.file_path  = "U" + URI
    new_task.bitrate    = bitrate
    new_task.width      = width
    new_task.height     = height
    new_task.priority   = priority
    new_task.start_time = int(time.time())
    new_task.progress   = 10

    task_status[task_id] = new_task
    preproc_queue.put_nowait(new_task)

    log_msg = 'new task, id: %s, priority: %s' % \
            (new_task.task_id, new_task.priority)
    logger.info(log_msg)
    print dump_msg(TASKID = task_id, PROGRESS = 10)
    sys.stdout.flush()

    return task_id

'''
query the status of a task, for RPC calling
'''
def get_progress(task_id):
    work_path = config.master_path
    f_name = os.path.join(work_path, task_id + '.pkl')
    if os.path.isfile(f_name) == True:
        pkl_file = open(f_name, 'rb')
        task = pickle.load(pkl_file)
        pkl_file.close()
        return task.progress

    if task_id in task_status.keys():
        try:
            task = task_status[task_id]
            return task.progress
        except:
            return -11
    return -10

'''
get target files of the transcoded video file.
'''
def get_target_file(task_id):
    work_path = config.master_path
    f_name = os.path.join(work_path, task_id + '.pkl')
    if os.path.isfile(f_name) == True:
        pkl_file = open(f_name, 'rb')
        task = pickle.load(pkl_file)
        pkl_file.close()

        width  = task.width.replace(' ', '').split('%')
        width  = filter(lambda a: a != '', width)
        height = task.height.replace(' ', '').split('%')
        height = filter(lambda a: a != '', height)

        f_list = ''
        for i in range(len(width)):
            f_path = ''
            res = width[i] + 'x' + height[i]
            f_path = os.path.join(work_path, \
                    task_id + '_' + res + '.mp4')
            f_list = f_list + f_path + '%'
        return f_list
    else:
        return None

'''
get the current number of blocks in dispatching queue
'''
def get_blk_num():
    return disb_queue.qsize()

'''
task scheduling and block dispatching:
1. determine the executation sequence
2. block dispatching
'''
class task_scheduling(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.times = 0
        #the number of VM instances
        #self.machine_num = config.machine_num

    def task_to_block(self, task, block):
        block.task_id      = task.task_id
        block.bitrate      = task.bitrate
        block.width        = task.width
        block.height       = task.height

    def scheduling(self):
        '''
        if config.sch_alg == 'vbs' or config.sch_alg == 'hvs':
            self.times = self.times + 1
            if self.times % 10 == 0:
                try:
                    #ret = red_con.get('server_num')
                    if ret == None:
                        self.machine_num = config.machine_num
                    else:
                        self.machine_num = int(ret)
                except:
                    self.machine_num = config.machine_num

            t = time.time()
            print 'machine num:', self.machine_num
            schedule_task[config.sch_alg](sched_queue, t, self.machine_num)
        else:
        '''

        schedule_task[config.sch_alg](sched_queue)

        if get_blk_num() < 2 and len(sched_queue) > 0:
            task = sched_queue.pop(0)
            msg = "%s: pop task for partition" % task.task_id
            db_update_start_time(task.task_id)
            self.dispatch(task)

    def det_seg_dur(self, task):
        return config.equal_block_dur

        '''
        if task.est_time <= 0:
            return config.equal_trans_dur

        blk_dur = (config.equal_trans_dur * task.v_duration) / task.est_time
        logger.info('duration: %f, estimated time: %f, block duration: %f', \
                task.v_duration, task.est_time, blk_dur)
        return blk_dur
        '''

    def dispatch(self, task):
        '''
        The video segment command should be:
        ffmpeg -i china.mp4 -f segment -segment_time 10 -c copy -map 0 \
            -segment_list china.list china%03d.mp4
        '''
        seg_dur         = self.det_seg_dur(task)
        file_path       = task.file_path
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
        logger.info('video segmentation result: %s', ret)
        if ret != 0:
            task.progress = -1
            return

        lines = ""
        with open(list_file_path) as f:
            lines = f.readlines()
            task.block_num = len(lines)
            task.progress  = 20
            print dump_msg(TASKID = task.task_id, PROGRESS = 20)
            sys.stdout.flush()

        index = 0
        for line in lines:
            block_info = block()
            line = line.strip('\n')
            self.task_to_block(task, block_info)
            block_info.file_path = os.path.join(work_path, line)
            block_info.path_len  = len(block_info.file_path)
            block_info.block_no  = index
            block_info.total_no  = len(lines)
            block_info.size      = os.path.getsize(block_info.file_path)

            f = open(block_info.file_path, 'rb')
            data = f.read()
            f.close()
            key = md5.new()
            key.update(data)
            block_info.md5_val = key.hexdigest()

            #put the video blocks into the queue for dispatching
            disb_queue.put(block_info)
            index = index + 1
        logger.info('all blocks have been put into the dispatching queue')


    def run(self):
        logger.debug('start worker for task scheduling')
        while True:
            self.scheduling()
            time.sleep(3)

'''
preprocess the task, download the video file
and estimate the transcoding time, etc.
'''
class preproc_thread(threading.Thread):
    def __init__(self, index):
        threading.Thread.__init__(self)
        self.index = index


    def trans_time_est(self, task):
        path = task.file_path
        info = self.c.probe(path)
        o_w = info.video.video_width
        o_h = info.video.video_height
        r_1 = int(o_w) * int(o_h)
        o_f = info.video.video_fps
        o_b = info.video.bitrate
        o_d = info.format.duration
        task.v_duration = o_d

        width   = task.width
        height  = task.height
        width   = width.replace(' ', '').split('%')
        width   = filter(lambda a: a != '', width)
        height  = height.replace(' ', '').split('%')
        height  = filter(lambda a: a != '', height)
        r_2     = int(width[0]) * int(height[0])

        f   = [[o_d, r_1, o_f, o_b, r_2]]
        out = self.net.sim(f)
        out = self.norm_t.renorm(out)
        out = out[0][0]
        log_msg = '%s: estimated time %f, %d, %f, %f, %d, %f' \
                % (task.task_id, o_d, r_1, o_f, o_b, r_2, out)
        logger.info(log_msg)
        return out

    def preprocess(self, task):
        file_path = ''
        if task.file_path[0] != 'L' and task.file_path[0] != 'U':
            task.progress = -1
            return -1

        if task.file_path[0] == 'L':
            file_path = task.file_path[1:]
        elif task.file_path[0] == 'U':
            url = task.file_path[1:]
            file_path = download_video(url, task.task_id)
            if file_path == '':
                task.progress = -1
                return -1

        task.file_path = file_path
        return 0

    def run(self):
        logger.debug('start worker for preprocessing: %s', self.index)
        while True:
            task = preproc_queue.get(True)
            log_msg = '%s: worker %s got task for preprocessing' % (task.task_id, self.index)
            logger.debug(log_msg)
            ret = self.preprocess(task)
            if ret == 0:
                sched_queue.append(task)
                log_msg = '%s: added into scheduling queue' % task.task_id
                logger.debug(log_msg)

'''
sending video blocks to the workers
'''
class send_data(SocketServer.BaseRequestHandler):
    def handle(self):
        logger.debug('accept request from worker for obtaining video block')
        block   = None
        try:
            block  = disb_queue.get_nowait()
            f      = open(block.file_path, 'rb')
            data   = f.read(); f.close()
            pack   = pack_block_info(block)
            data_block = pack + data
            logger.debug('data block length: %s', len(data_block))

            sum = 0; flag = 0
            while True:
                cnt = self.request.send(data_block[sum: sum + 1024*400])
                sum = cnt + sum
                if cnt == 0:
                    logger.debug('the number of bytes sent: %s', sum)
                    self.request.shutdown(socket.SHUT_WR)
                    break
                if cnt < 0:
                    flag = -1
                    break

            if flag == 0:
                ret_msg = self.request.recv(10)
                logger.debug('the return msg is: %s', ret_msg)
                if ret_msg == 'okay':
                    logger.debug('send data to the worker successfully')
                else:
                    flag = -1
            if flag == -1:
                disb_queue.put(block)
                logger.error('fail to send the data to the worker, put back the task')

        except Queue.Empty:
            logger.error('no task in Queue')
        except Exception, ex:
            if block != None:
                disb_queue.put(block)
            logger.error('fail to send data, retry')
        finally:
            self.request.close()

'''
multi-thread class for block dispatching
'''
class send_data_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        logger.debug('start the thread for sending video block')
        server = ThreadedTCPServer((master_ip, master_snd_port), send_data)
        server.serve_forever()

'''
receiving data from the worker
'''
class recv_data(SocketServer.BaseRequestHandler):
    def write_file(self, block_info, data_block):
        cur = 0; num = 0
        fs  = [0, 0, 0, 0, 0, 0]
        (num, fs[0], fs[1], fs[2], fs[3], fs[4], fs[5]) = \
                struct.unpack(format_length, data_block[0:struct.calcsize(format_length)])
        cur = cur + struct.calcsize(format_length)

        base_name = os.path.basename(block_info.file_path)
        base_name = base_name.replace('_package', '')
        (prefix,suffix) = os.path.splitext(base_name)
        width  = block_info.width.replace(' ', '').split('%')
        width  = filter(lambda a: a != '', width)
        height = block_info.height.replace(' ', '').split('%')
        height = filter(lambda a: a != '', height)
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
        logger.debug('receiving data from worker')

        try:
            while True:
                data = self.request.recv(1024*400)
                data_block = data_block + data
                if flag == 0 and len(data_block) >= struct.calcsize(block_format):
                    flag = 1
                    unpack_block_info(block_info, data_block)
                if not data:
                    break

            if flag == 0:
                success = 0
                logger.error('cannot decode the header')
                return

            if block_info.size == len(data_block) - struct.calcsize(block_format):
                msg = "%s: received data's size is okay" % block_info.task_id
                logger.debug(msg)
            else:
                logger.debug('received data: length error')
                success = 0
                return

            key = md5.new()
            key.update(data_block[struct.calcsize(block_format):])
            val = key.hexdigest()
            if block_info.md5_val == val:
                msg = '%s: md5 check is okay' % block_info.task_id
                logger.debug(msg)
                self.request.sendall('okay')
                self.request.shutdown(socket.SHUT_WR)

                path_len  = block_info.path_len
                base_name = os.path.basename(block_info.file_path[0:path_len])
                new_path  = os.path.join(work_path, base_name)
                block_info.file_path = new_path
                block_info.path_len  = len(new_path)
                task_id   = block_info.task_id
                block_id  = block_info.block_no

                #check whehter the transcoding task is successful
                task_stat = task_status[task_id]
                if block_info.status == 0 and task_stat.progress > 0:
                    if block_id in task_stat.block.keys():
                        task_stat.block[block_id] = block_info
                    else:
                        task_stat.fin_num   += 1
                        task_stat.progress  += 70.0/task_stat.block_num
                        print dump_msg(TASKID = task_id, PROGRESS = task_stat.progress)
                        sys.stdout.flush()
                        task_stat.block[block_id] = block_info
                else:
                    success = 0
                    task_stat.progress = -2

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
            self.request.sendall('fail')
            success = 0
        finally:
            self.request.close()
            if success == 1:
                return block_info
            else:
                return None


'''
multithread class for receiving data from workers
'''
class recv_data_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        logger.debug('start the receiving data thread')
        server = ThreadedTCPServer((master_ip, master_rev_port), recv_data)
        server.serve_forever()

'''
check whether a task has been finished
'''
class task_tracker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def write_pkl(self, task_id, task):
        work_path = config.master_path
        f_name = os.path.join(work_path, task_id + '.pkl')
        output = open(f_name, 'wb')
        pickle.dump(task, output)
        output.close()

    def combine_blocks(self, video_files, path_out_file):

        mp4box_path = 'MP4Box'

        # First delete the existing out video file
        if os.path.exists(str(path_out_file)):
            os.remove(str(path_out_file))

        # Construct the args to mp4box
        prog_args = [mp4box_path]
        for video_file in video_files:
            prog_args.append("-cat")
            prog_args.append(str(video_file))

        # prog_args.append("-isma")

        prog_args.append("-new")
        # Add the output file at the very end
        prog_args.append(str(path_out_file))

        # Run the app and collect the output
        ret = subprocess.Popen(prog_args,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        longest_line = 0
        while True:
            try:
                line = ret.stdout.readline()
                if not line:
                    break
                line = line.strip()[
                       :65]  # Limit the max length of the line, otherwise it will screw up our console window
                longest_line = max(longest_line, len(line))
                sys.stdout.write('\r ' + line.ljust(longest_line))
                sys.stdout.flush()
            except UnicodeDecodeError:
                continue  # Ignore all unicode errors

        # Ensure that the return code was ok before continuing
        retcode = ret.poll()
        while retcode is None:
            retcode = ret.poll()

        logger.info('MP4Box concat return code: %s', retcode)

        # Move the input to the beginning of the line again
        # subsequent output text will look nicer :)
        sys.stdout.write('\r')
        return retcode

    def concat_block(self, task):
        logger.debug("%s: concatenate the blocks" % task.task_id)
        total_no = task.block_num
        width    = task.width.replace(' ', '').split('%')
        width    = filter(lambda a: a != '', width)
        height   = task.height.replace(' ', '').split('%')
        height   = filter(lambda a: a != '', height)

        suf     = ''
        task_id = task.task_id
        block_list = []
        for i in range(len(width)):
            resolution = width[i] + 'x' + height[i]
            list_path  = os.path.join(config.master_path,
                                      task_id + '_' + resolution + '.list')
            f = open(list_path, 'w')
            for i in range(0, total_no):
                path        = task.block[i].file_path
                dir_name    = os.path.dirname(path)
                base_name   = os.path.basename(path)
                base_name   = base_name.replace('_package', '')
                (pre, suf)  = os.path.splitext(base_name)
                file_name   = os.path.join(dir_name, pre + resolution + suf)
                block_list.append(file_name)
                line = 'file ' + '\'' + file_name + '\'' + '\n'
                f.write(line)
            f.close()

            new_file = os.path.join(config.master_path,
                                    task_id + '_' + resolution + suf)
            ret = self.combine_blocks(block_list, new_file)

            if ret is not 0:
                logger.error("Error while concatenating file")
                return ret
        return 0

    def run(self):
        while True:
            #print 'current number of ongoing tasks:', len(task_status)
            #print 'current number of blocks in queue:', get_blk_num()
            time.sleep(2)

            task = None
            for task_id in task_status.keys():
                task = task_status[task_id]
                if task.fin_num == task.block_num and task.block_num > 0:
                    ret = 0
                    try:
                        ret = self.concat_block(task)
                    except:
                        ret = -1

                    if ret == 0:
                        task.progress = 100
                        print dump_msg(TASKID = task_id, PROGRESS = 100)
                        sys.stdout.flush()
                        cur_time = time.time()
                        dur_time = cur_time - task.start_time
                        logger.info('transcoding duration: %s', dur_time)
                        db_update_finish_time(task_id, 0)
                    else:
                        task.progress = -3
                        db_update_finish_time(task_id, -3)

                    #write the task information to file
                    self.write_pkl(task_id, task)
                    #pop the task from the task list
                    logger.debug("%s: task has been finished" % task_id)
                    task_status.pop(task_id)
                    # Indicate that a formerly enqueued task is complete
                    preproc_queue.task_done()
                    continue

                if task.progress < 0:
                    task_status.pop(task_id)
                    self.write_pkl(task_id, task)
                    db_update_finish_time(task_id, task.progress)
                    continue

#check whether the task has been time out
class block_tracker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def check_blocks(self):
        pass

    def run(self):
        while True:
            check_blocks()

'''
log module for XML RPC
'''
class RequestHandler(SimpleXMLRPCRequestHandler):
    def log_message(self, format, *args):
        pass

'''
main program: start up each of the threads
'''
if __name__ == '__main__':

    #register the logger
    logger = init_log_module("master", master_ip, logging.DEBUG)
    logger.debug('start the master server')

    #check the work path
    work_path = config.master_path
    if os.path.exists(work_path) == False:
        logger.critical('work path for master does not exist:%s', work_path)
        sys.exit()

    #create database and init the tables
    ret = init_db()
    if ret == -1:
        logger.error('cannot initialize the database for master')


    #start the rpc thread to handle the request
    server = master_rpc_server((master_ip, master_rpc_port), \
             requestHandler = RequestHandler, allow_none=True)
    # Register a function that can respond to XML-RPC requests
    server.register_function(put_trans_task, "put_trans_task")
    server.register_function(get_progress, "get_progress")
    server.register_function(get_target_file, "get_target_file")
    server.register_function(get_blk_num, "get_blk_num")

    #create the thread for preprocessing video files
    preproc_num = config.preproc_thread_num
    for i in range(preproc_num):
        t = preproc_thread(i)
        t.start()

    #create the thread for task scheduling
    t = task_scheduling()
    t.start()

    #create the thread for sending data blocks to the worker
    t = send_data_thread()
    t.start()

    #create the thread for receiving the data blocks from the workers
    t = recv_data_thread()
    t.start()

    #create the thread for checking tasks
    t = task_tracker()
    t.start()

    #create the thread for checking the block status
    '''
    t = block_tracker()
    t.start()
    '''

    #never stop
    server.serve_forever()


