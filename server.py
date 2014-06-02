import sys
import md5
import time
import struct
import gevent
from gevent import socket


def server(port):
    s = gevent.socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)

    #print s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    #print s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

    s.bind(('0.0.0.0', port))
    s.listen(500)

    while True:
        cli, addr = s.accept()
        gevent.spawn(handle_request, cli, gevent.sleep)


def handle_request(s, sleep):
    size = 0
    flag = 0
    content = ''
    format = '32sq'

    try:
        while True:
            data = s.recv(1024*400)
            content = content + data
            if flag == 0 and len(content) > 40:
                flag = 1
                md5_val, size = struct.unpack(format, content[0:40])

            if not data:
                break

        if size == len(content) - 40:
            print 'success'
        else:
            print 'error'

        key = md5.new()
        key.update(content[40:])
        val = key.hexdigest()

        print len(val)
        print len(md5_val)

        if md5_val == val:
            print 'md5 check okay'
        else:
            print val
            print md5_val
            print 'md5 check fail'

    except Exception, ex:
        print ex

    finally:
        s.close()

if __name__ == '__main__':
    server(7777)
