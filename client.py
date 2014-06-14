from xmlrpclib import ServerProxy

server = ServerProxy("http://localhost:8089")
print server.add_task("/home/guanyu/Project/distributed_transcoding/distributed.mp4", 10, 10, 10)
