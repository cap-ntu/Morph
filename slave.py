import os
import md5
import struct
import gevent
import subprocess
from common import *
from gevent import socket
from xmlrpclib import ServerProxy

working_path = "/tmp/"

def recv_data( ):
    flag        = 0
    content     = ''
    success     = 0
    new_block   = block()
    format      = "8si200siiiiii32s"

    s = gevent.socket.socket()         # Create a socket object
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024*10)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*10)

    s.connect((host, port))

    try:
        while True:
            data = s.recv(1024*400)
            content = content + data
            if flag == 0 and len(content) >= struct.calcsize(format):
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
                 new_block.md5_val)   = struct.unpack(format, content[0:struct.calcsize(format)])

            if not data:
                break


        if new_block.size == len(content) - struct.calcsize(format):
            print 'length okay'
        else:
            print new_block.size
            print len(content) - struct.calcsize(format)
            print 'length error'
            return None

        key = md5.new()
        key.update(content[struct.calcsize(format):])
        val = key.hexdigest()

        if new_block.md5_val == val:
            print 'md5 check okay'
            path_len    = new_block.path_len
            base_name   = os.path.basename(new_block.file_path[0:path_len])
            new_path    = working_path + base_name

            new_block.file_path = new_path
            new_block.path_len  = len(new_path)


            f = open(new_path, 'wb')
            f.write(content[struct.calcsize(format):])
            f.close()
            s.send('okay')
            sucess = 1
        else:
            print 'md5 check fail'
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

def transcode_data(new_block):
    print 'transcode the video block into user requested format'
    print new_block.task_id
    print new_block.file_path

    dir_name        = os.path.dirname(new_block.file_path)
    base_name       = os.path.basename(new_block.file_path)
    (prefix,suffix) = os.path.splitext(base_name)
    new_path        = dir_name + '/' + prefix + '_new' + suffix

    cmd = "ffmpeg -y -i " + new_block.file_path + " -threads 4 -s 600x300 -strict -2 " + new_path

    print cmd
    #os.system(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #for line in p.stdout.readlines():
    #    print line,
    retval = p.wait()

    #we still to check the result at here
    f       = open(new_path, 'rb')
    data    = f.read()
    f.close()

    key     = md5.new()
    key.update(data)
    md5_val = key.hexdigest()

    size    = os.path.getsize(new_path)

    new_block.file_path = new_path
    new_block.path_len  = len(new_path)
    new_block.size      = size
    new_block.md5_val   = md5_val


    return (0, new_block)


def send_back_data(new_block):
    print 'send back the file:'
    try:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024*10)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*10)

        host = "localhost"          # Get local machine name
        port = 8888                 # Reserve a port for your service.

        s.connect((host, port))

        f       = open(new_block.file_path, 'rb')
        data    = f.read()
        f.close()

        pack    = pack_block_info(new_block)
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


if __name__ == '__main__':

    host = "localhost"                 # Get local machine name
    port = 7777                        # Reserve a port for your service.

    server = ServerProxy("http://localhost:8089")

    while True:

        num = server.get_blk_num()
        print num
        if num == 0:
            gevent.sleep(5)
            continue

        new_block     =   recv_data()
        (ret, new_block)  =   transcode_data(new_block)
        if ret == 0:
            send_back_data(new_block)

