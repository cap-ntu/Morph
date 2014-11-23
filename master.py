import os
import md5
import struct
import threading
import subprocess
import SocketServer
from common import *
from random import Random
from SocketServer import ThreadingMixIn
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler


tasks_queue = {}
#the original videos which needs to be split into blocks
split_queue = Queue(maxsize = 100)
#the video blocks after slicing
block_queue = Queue(maxsize = 10000)

#the lock used to access the tasks_queue
sem = BoundedSemaphore(1)

class master_rpc_server(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class ThreadedTCPServer(ThreadingMixIn, SocketServer.TCPServer):
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


class task:
    def __init__(self):
        self.task_id    = ""
        self.file_path  = ""
        self.bitrate    = -1
        self.width      = -1
        self.height     = -1
        self.num        = -1

'''
task status: 0, 1, 2

'''

class task_status:
    def __init__(self):
        self.block      = None
        self.status     = 0



def add_trans_task(file_path, bitrate, width, height):

    key_val             = gen_key()
    new_item            = task()

    new_item.task_id    = key_val
    new_item.file_path  = file_path
    new_item.bitrate    = bitrate
    new_item.width      = width
    new_item.height     = height
    new_item.num        = -1
    split_queue.put_nowait(new_item)
    print 'put the task into the queue'

    sem.acquire()
    tasks_queue[key_val] = {}
    sem.release()

    return 0

def query_result(task_id):
    pass


class split_thread(threading.Thread):

    def __init__(self, lock):
        threading.Thread.__init__(self)
        self.lock   = lock

    '''
    This function is used to split the video into segments:
    The video segment command should be:
    ffmpeg -i china.mp4 -f segment -segment_time 10 -c copy -map 0 \
            -segment_list china.list china%03d.mp4
    '''

    def split_video(item):
        seg_time        = 60 * 30
        file_path       = item.file_path
        base_name       = os.path.basename(file_path)
        dir_name        = os.path.dirname(file_path)
        (prefix,suffix) = os.path.splitext(base_name)

        cmd = "ffmpeg -i " + file_path + " -f segment -segment_time " + str(seg_time) + \
                " -c copy -map 0 -segment_list " + prefix + ".list " + prefix + "%03d" + suffix
        print cmd
        #os.system(cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #for line in p.stdout.readlines():
        #    print line,
        retval = p.wait()

        f = open(prefix + ".list")
        lines = f.readlines()

        index = 0
        for line in lines:
            new_block = block()
            line = line.strip('\n')

            new_block.task_id       = item.task_id
            new_block.file_path     = dir_name + '/' + line
            new_block.path_len      = len(new_block.file_path)
            new_block.block_no      = index
            new_block.total_no      = len(lines)
            new_block.bitrate       = item.bitrate
            new_block.width         = item.width
            new_block.height        = item.height
            new_block.size          = os.path.getsize(new_block.file_path)

            print new_block.file_path
            print new_block.size
            f       = open(new_block.file_path, 'rb')
            data    = f.read()
            f.close()

            key     = md5.new()
            key.update(data)
            md5_val = key.hexdigest()

            new_block.md5_val = md5_val
            print md5_val

            block_queue.put(new_block)
            index = index + 1

    def run(self):
        while True:
            task = split_queue.get(True)
            #print('Worker %s got task %s' % (n, item.task_id))
            split_video(task)


def get_blk_num():
    return block_queue.qsize()


def send_data(s, sleep):
    try:
        block   = block_queue.get_nowait()

        f       = open(block.file_path, 'rb')
        data    = f.read()
        f.close()

        pack    = pack_block_info(block)
        content = pack + data
        print 'content length:', len(content)

        sum = 0
        while True:
            cnt = s.send(content[sum: sum + 1024*400])
            # print cnt
            sum = cnt + sum
            if cnt == 0:
                print 'finished:', sum
                break

        s.shutdown(gevent.socket.SHUT_WR)
        ret_msg = s.recv(10)
        print 'the return msg is:', ret_msg

        s.close()

    except Exception, ex:
        print ex
        s.close()

def send_data_server(port):
    s = gevent.socket.socket()
    s.setsockopt(gevent.socket.SOL_SOCKET, gevent.socket.SO_RCVBUF, 1024*1024)
    s.setsockopt(gevent.socket.SOL_SOCKET, gevent.socket.SO_SNDBUF, 1024*1024)

    #print s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    #print s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

    s.bind(('0.0.0.0', port))
    s.listen(500)

    while True:
        cli, addr = s.accept()
        gevent.spawn(send_data, cli, gevent.sleep)


class send_data_thread(threading.Thread):

    def __init__(self, lock, index):
        threading.Thread.__init__(self)
        self.lock   = lock
        self.index  = index

    def run(self):
        server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
        server.serve_forever()


def recv_data(s, sleep):

    flag        = 0
    content     = ''
    success     = 0
    new_block   = block()
    working_path = '/tmp/server/'

    print 'begin to receive data from client'

    try:
        while True:
            data = s.recv(1024*400)
            content = content + data
            if flag == 0 and len(content) >= struct.calcsize(block_format):
                flag = 1
                (new_block.task_id,   \
                 new_block.path_len,  \
                 new_block.file_path, \
                 new_block.block_no,  \
                 new_block.total_no,  \
                 new_block.bitrate,   \
                 new_block.width,     \
                 new_block.height,    \
                 new_block.size,      \
                 new_block.md5_val)   = struct.unpack(block_format, content[0:struct.calcsize(block_format)])

            if not data:
                break

        if new_block.size == len(content) - struct.calcsize(block_format):
            print 'received data: length okay'
        else:
            print new_block.size
            print len(content) - struct.calcsize(block_format)
            print 'received data: length error'
            return None

        key = md5.new()
        key.update(content[struct.calcsize(block_format):])
        val = key.hexdigest()

        if new_block.md5_val == val:
            print 'received data: md5 check okay'
            path_len    = new_block.path_len
            base_name   = os.path.basename(new_block.file_path[0:path_len])
            new_path    = working_path + base_name

            new_block.file_path = new_path
            new_block.path_len  = len(new_path)

            new_task = task_status()
            new_task.block  = new_block
            new_task.status = 2

            task_id     = new_block.task_id
            block_id    = new_block.block_no

            sem.acquire()
            tasks           = tasks_queue[task_id]
            tasks[block_id] = new_task
            sem.release()

            f = open(new_path, 'wb')
            f.write(content[struct.calcsize(block_format):])
            f.close()
            s.send('okay')
            sucess = 1
        else:
            print 'received data: md5 check fail'
            s.send('fail')
            sucess = 0


    except Exception, ex:
        print ex
        s.send('fail')
        sucess = 0
    finally:
        s.close()
        if sucess == 1:
            return new_block
        else:
            return None


def receiver(port):
    s = gevent.socket.socket()
    s.setsockopt(gevent.socket.SOL_SOCKET, gevent.socket.SO_RCVBUF, 1024*1024)
    s.setsockopt(gevent.socket.SOL_SOCKET, gevent.socket.SO_SNDBUF, 1024*1024)

    #print s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    #print s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

    s.bind(('0.0.0.0', port))
    s.listen(500)

    while True:
        cli, addr = s.accept()
        gevent.spawn(recv_data, cli, gevent.sleep)


def concat_block(task):
    print 'concatenate the blocks:'
    total_no    = task[0].block.total_no
    file_path   = task[0].block.file_path

    dir_name    = os.path.dirname(file_path)
    task_id     = task[0].block.task_id
    list_name   = dir_name + '/' + task_id + '.list'
    new_file    = dir_name + '/' + task_id + '.mp4'

    f = open(list_name, 'w')
    for key in range(0, total_no):
        line = 'file ' + '\'' + task[key].block.file_path + '\'' + '\n'
        print line
        f.write(line)
    f.close()

    cmd = 'ffmpeg -f concat -i ' + list_name + ' -c copy ' + new_file
    os.system(cmd)



def task_status_checker():
    while True:
        sem.acquire()
        task = None
        print 'current task number:', len(tasks_queue)
        for task_id in tasks_queue.keys():
            task = tasks_queue[task_id]
            blk_no = len(task.keys())

            if blk_no > 0:
                block_0 = task[task.keys()[0]].block
                if blk_no == block_0.total_no:
                    print 'job finished'
                    tasks_queue.pop(task_id)
                    concat_block(task)
        sem.release()
        gevent.sleep(5)


if __name__ == '__main__':

    master_ip       = config.master_ip
    master_rpc_port = config.master_rpc_port
    master_rev_port = config.master_rev_port
    master_snd_port = config.master_snd_port

    #start the rpc thread to handle the request
    server = master_rpc_server((master_ip, int(master_rpc_port)))
    server.register_function(add_trans_task, "add_trans_task")
    server.register_function(query_result, "query_result")
    server.register_function(get_blk_num,  "get_blk_num")

    #create the thread for splitting video files
    for i in range(3):
        t = trans_thread(lock, i)
        t.start()

    #create the thread for sending data blocks to the worker
    t = send_data_thread()
    t.start()

    t = recv_data_thread()
    t.start()

    gevent.spawn(task_status_checker)

    server.serve_forever()



