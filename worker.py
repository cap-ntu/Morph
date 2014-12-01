import os
import sys
import md5
import time
import socket
import config
import struct
import logging
import subprocess
import xmlrpclib
from common import *

logger = None

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
                 block_info.md5_val,   \
                 block_info.status,    \
                 block_info.priority)   = struct.unpack(block_format, block_data[0:struct.calcsize(block_format)])

            if not data:
                break

        if flag == 0:
            logger.error('fail to decode the header')
            s.send('fail')
            success = 0
            return

        key = md5.new()
        key.update(block_data[struct.calcsize(block_format):])
        val = key.hexdigest()

        if block_info.md5_val == val:
            s.send('okay')
            s.shutdown(socket.SHUT_WR)
            logger.info('%s: the MD5 checking of the received data block is okay', \
                    block_info.task_id)

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
            logger.info('%s: md5 check fail', block_info.task_id)
            success = 0

    except Exception, ex:
        #print ex
        s.send('fail')
        logger.error('fail to receive data from the master')
        success = 0
    finally:
        s.close()
        if success == 1:
            return block_info
        else:
            return None


def transcode_data(block_info):
    logger.debug('%s: transcode the video block into the user requested format',\
            block_info.task_id)

    dir_name        = os.path.dirname(block_info.file_path)
    base_name       = os.path.basename(block_info.file_path)
    (prefix,suffix) = os.path.splitext(base_name)
    new_path        = os.path.join(dir_name, prefix + '_new' + suffix)
    resolution      = block_info.width + 'x' + block_info.height

    cmd = "ffmpeg -y -i " + block_info.file_path + " -s " + resolution + " -strict -2 " + new_path
    logger.debug('%s: %s', block_info.task_id, cmd)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    ret = p.returncode
    block_info.status = ret
    log_msg = 'the return code is: %s' % ret
    logger.info('%s: %s', block_info.task_id, log_msg)

    data = ""
    if ret == 0:
        f    = open(new_path, 'rb')
        data = f.read()
        f.close()

    key = md5.new()
    key.update(data)
    md5_val = key.hexdigest()
    block_info.md5_val = md5_val

    if ret == 0:
        size = os.path.getsize(new_path)
        block_info.file_path = new_path
        block_info.path_len  = len(new_path)
        block_info.size      = size
    else:
        block_info.file_path = ""
        block_info.path_len  = 0
        block_info.size      = 0

    return block_info


def send_back_data(block_info, master_ip, master_rev_port):
    logger.debug('%s: send back the transcoded video block to the master', \
            block_info.task_id)

    try:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024*10)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*10)
        s.connect((master_ip, master_rev_port))

        data = ""
        if block_info.status == 0:
            f    = open(block_info.file_path, 'rb')
            data = f.read()
            f.close()

        pack = pack_block_info(block_info)
        block_data = pack + data
        logger.debug('the file length of the sent back video block: %s', \
                len(block_data))

        sum = 0
        while True:
            cnt = s.send(block_data[sum: sum + 1024*400])
            sum = cnt + sum
            if cnt == 0:
                logger.debug('the length of the sent back data: %s', sum)
                break
        s.shutdown(socket.SHUT_WR)

        ret_msg = s.recv(10)
        s.close()
        logger.debug('the return msg is: %s', ret_msg)

        if ret_msg == 'okay':
            return 0
        else:
            return -1

    except Exception, ex:
        logger.debug('fail to send back video block information')
        s.close()
        return -1


if __name__ == '__main__':

    host_name = socket.gethostname()
    host_name = host_name.replace(" ", "").lower()
    if len(host_name) == 0:
        host_name = "localhost"

    logger = init_log_module("worker", host_name, logging.DEBUG)
    logger.debug('start the worker')

    work_path = config.worker_path
    if os.path.exists(work_path) == False:
        logger.critical('work path does not exist:%s', work_path)
        sys.exit()

    master_ip       = config.master_ip
    master_rpc_port = config.master_rpc_port
    master_rev_port = int(config.master_rev_port)
    master_snd_port = int(config.master_snd_port)

    rpc_addr = "http://" + master_ip + ":" + master_rpc_port
    server   = xmlrpclib.ServerProxy(rpc_addr)

    while True:
        num = server.get_blk_num()
        logger.debug('The current number of blocks in the master: %s', num)
        if num == 0:
            time.sleep(1)
            continue

        block_info = recv_data_block(master_ip, master_snd_port)
        if block_info is not None:
            logger.debug('%s: obtain the data block from the master successfully',\
                    block_info.task_id)
            block_info = transcode_data(block_info)
        else:
            logger.error('fail to get data block from the master')
            continue

        #send back the transcoded video, the content depends on whether
        #it has succeed
        try_times = 0
        while try_times < 3:
            ret = send_back_data(block_info, master_ip, master_rev_port)
            if ret == 0:
                break
            else:
                try_times += 1




