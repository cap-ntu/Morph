import os
import md5
import time
import socket
import config
import struct
import subprocess
import xmlrpclib
from common import *

def recv_data_block(master_ip, master_snd_port):
    flag        = 0
    success     = 0
    block_data  = ''
    block_info  = block()
    work_path   = config.worker_path

    s = socket.socket()         # Create a socket object
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024*10)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*10)

    s.connect((master_ip, master_snd_port))

    try:
        while True:
            data = s.recv(1024*400)
            block_data = block_data + data

            if flag == 0 and len(block_data) >= struct.calcsize(block_format):
                flag = 1
                (block_info.task_id,   \
                 block_info.path_len,  \
                 block_info.file_path, \
                 block_info.block_no,  \
                 block_info.total_no,  \
                 block_info.bitrate,   \
                 block_info.width,     \
                 block_info.height,    \
                 block_info.size,      \
                 block_info.md5_val,
                 block_info.status)   = struct.unpack(block_format, block_data[0:struct.calcsize(block_format)])

            if not data:
                break

        #check the md5 value of the received data
        key = md5.new()
        key.update(block_data[struct.calcsize(block_format):])
        val = key.hexdigest()

        if block_info.md5_val == val:
            s.send('okay')
            s.shutdown(socket.SHUT_WR)
            print 'the MD5 checking of the received data block is okay'

            path_len    = block_info.path_len
            base_name   = os.path.basename(block_info.file_path[0:path_len])
            new_path    = os.path.join(work_path, base_name)

            block_info.file_path = new_path
            block_info.path_len  = len(new_path)

            f = open(new_path, 'wb')
            f.write(block_data[struct.calcsize(block_format):])
            f.close()

            success = 1
        else:
            s.send('fail')
            s.shutdown(socket.SHUT_WR)
            print 'md5 check fail'
            success = 0

    except Exception, ex:
        print ex
        s.send('fail')
        success = 0

    finally:
        s.close()
        if success == 1:
            return block_info
        else:
            return None


def transcode_data(block_info):
    print 'transcode the video block into the user requested format'
    #print block_info.task_id
    #print block_info.file_path

    dir_name        = os.path.dirname(block_info.file_path)
    base_name       = os.path.basename(block_info.file_path)
    (prefix,suffix) = os.path.splitext(base_name)
    new_path        = os.path.join(dir_name, prefix + '_new' + suffix)
    resolution      = block_info.width + 'x' + block_info.height

    cmd = "ffmpeg -y -i " + block_info.file_path + " -s " + resolution + " -strict -2 " + new_path
    print cmd

    os.system(cmd)
    #p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #for line in p.stdout.readlines():
    #    print line,
    #retval = p.wait()
    #we still to check the result at here

    f    = open(new_path, 'rb')
    data = f.read()
    f.close()

    key = md5.new()
    key.update(data)
    md5_val = key.hexdigest()

    size = os.path.getsize(new_path)

    block_info.file_path = new_path
    block_info.path_len  = len(new_path)
    block_info.size      = size
    block_info.md5_val   = md5_val
    block_info.status    = 0

    return block_info


def send_back_data(block_info, master_ip, master_rev_port):
    print 'send back the transcoded video block to the master'

    try:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024*10)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*10)

        s.connect((master_ip, master_rev_port))

        f    = open(block_info.file_path, 'rb')
        data = f.read()
        f.close()

        pack = pack_block_info(block_info)
        block_data = pack + data
        print 'the file length of the sent back video block:', len(block_data)

        sum = 0
        while True:
            cnt = s.send(block_data[sum: sum + 1024*400])
            sum = cnt + sum
            if cnt == 0:
                print 'finish sending back data:', sum
                break

        s.shutdown(socket.SHUT_WR)

        ret_msg = s.recv(10)
        print 'the return msg is:', ret_msg
        s.close()

    except Exception, ex:
        print ex
        s.close()


if __name__ == '__main__':

    master_ip       = config.master_ip
    master_rpc_port = config.master_rpc_port
    master_rev_port = int(config.master_rev_port)
    master_snd_port = int(config.master_snd_port)

    rpc_addr = "http://" + master_ip + ":" + master_rpc_port
    server   = xmlrpclib.ServerProxy(rpc_addr)

    while True:
        num = server.get_blk_num()
        print "The current number of blocks in the master:", num
        if num == 0:
            time.sleep(1)
            continue

        block_info = recv_data_block(master_ip, master_snd_port)
        if block_info is not None:
            print 'obtain the data block from the master successfully'
            block_info = transcode_data(block_info)
        else:
            print 'fail to get data block from the master'
            continue

        if block_info.status == 0:
            send_back_data(block_info, master_ip, master_rev_port)




