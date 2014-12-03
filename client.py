import os
import sys
import config
import argparse
from common import *
from xmlrpclib import ServerProxy

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input video file', required=True)
    #parser.add_argument('-s', '--resolution', help='resolutions of the output video file', required=True)
    parser.add_argument('-p', '--priority', help='priority of the task')

    parser.add_argument('-s', '--resolution', nargs='*', help='resolutions of the output video file', required=True)
    #parser.add_argument('-o', '--output', help='output video file', required=True)
    args = parser.parse_args()
    input_file = args.input
    resolution = args.resolution
    priority   = args.priority
    file_path  = ''
    width      = ''
    height     = ''


    if os.path.isfile(input_file) == False:
        print 'error: input file does not exist'
        sys.exit(-1)
    else:
        file_path = input_file

    width   = ''
    height  = ''

    for res in resolution:
        r = res.split('x')
        if len(r) != 2:
            print 'error: resolution format is wrong'
            sys.exit(-1)

        if r[0].isdigit() == False or r[1].isdigit() == False:
            print 'error: resolution format is wrong'
            sys.exit(-1)

        width   += (r[0] + '%')
        height  += (r[1] + '%')

    width  = width.ljust(30)
    height = height.ljust(30)

    if priority == None:
        priority = 5
    else:
        priority = int(priority)

    master_ip       = config.master_ip
    master_rpc_port = config.master_rpc_port
    rpc_addr = "http://" + master_ip + ":" + master_rpc_port
    server = ServerProxy(rpc_addr)

    key = server.put_trans_task(file_path, "", width, height, priority)
    print key




