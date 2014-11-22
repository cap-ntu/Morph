import os
import md5
import socket
import time
import struct

s = socket.socket()         # Create a socket object
s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024*10)
s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*10)

print s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
print s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

host = "155.69.151.159"      # Get local machine name
port = 7777                 # Reserve a port for your service.
file_path = '/home/guanyu/Videos/lvjuren.mp4'

f = open(file_path, 'rb')
data    = f.read()
f.close()

key = md5.new()
key.update(data)
md5_val = key.hexdigest()

size = os.path.getsize(file_path)
print size

format = '32sq'
msg_head = struct.pack(format, md5_val, size)
data = msg_head + data

s.connect((host, port))

a = time.time()

sum = 0
while True:
    cnt = s.send(data[sum: sum + 1024*400])
    # print cnt
    sum = cnt + sum
    if cnt == 0:
        print 'finished:', sum
        break

b = time.time()



duration = b - a
speed = size / 1024 / 1024 / duration
print speed, 'MB/s'

f.close()
s.close()                     # Close the socket when done
