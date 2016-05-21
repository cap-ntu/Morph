'''
The command line interface for submitting transcoding tasks
'''

import os,sys
import config
import argparse
from common import *
from xmlrpclib import ServerProxy

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--input', help='input video file')
    parser.add_argument('-u', '--url',   help='input url')
    parser.add_argument('-t', '--id',    help='task id')
    parser.add_argument('-p', '--priority', help='task priority')
    parser.add_argument('-s', '--resolution', nargs='*', help='target resolutions', required=True)

    args = parser.parse_args()
    input_file = args.input
    input_url  = args.url
    task_id    = args.id
    priority   = args.priority
    resolution = args.resolution
    file_path  = ''
    width      = ''
    height     = ''

    if input_file == None and input_url == None:
        print 'error: specify a local file or a url'
        sys.exit(-1)
    if input_file != None and input_url != None:
        print 'error: you can only specify a local file or a url'
        sys.exit(-1)
    if input_file != None:
        _, ext = os.path.splitext(input_file)
        if ext != '.mp4':
            print 'The current verison only supports the input file in container of MP4'
            sys.exit(-1)
        if os.path.isfile(input_file) == False:
            print 'error: input file does not exist'
            sys.exit(-1)
        else:
            file_path = "L" + input_file

    if input_url != None:
        _, ext = os.path.splitext(input_url)
        if ext != '.mp4':
            print 'The current verison only supports the input file in container of MP4'
            sys.exit(-1)
        file_path = "U" + input_url

    if task_id != None and len(task_id) > 50:
        print 'error: the length of the task id cannot exceed 50'
        sys.exit(-1)

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
    server = ServerProxy(rpc_addr, allow_none=True)
    key = server.put_trans_task(file_path, "", width, height, priority, task_id)
    print key




