import sys
import md5
import time
import struct
import SocketServer

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        size = 0
        flag = 0
        content = ''
        format = '32sq'

        try:
            while True:
                data = self.request.recv(1024*400)
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
            pass


if __name__ == '__main__':
    HOST, PORT = "155.69.151.159", 7777
    server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()


