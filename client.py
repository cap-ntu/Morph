import config
from common import *
from xmlrpclib import ServerProxy

if __name__ == "__main__":

    master_ip   = config.master_ip
    master_port = config.master_port
    master_addr = "http://" + master_ip + ":" + master_port
    server = ServerProxy(master_addr)

    #please replace it with the program command line
    file_path = '/home/guanyu/Project/hope/lvjuren.mp4'
    width     = 400
    height    = 400

    ret = server.add_task(file_path, width, height)

