'''
The command line interface for querying task progress and system state
Usage:
    -k: keyid, get the transcoding progress of a task specified by the keyid
    -n: none,  get the current number of video blocks in the queue
'''

import os
import sys
import config
import argparse
from common import *
from xmlrpclib import ServerProxy

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', help='task key', required=False)
    parser.add_argument('-n', '--num', action='store_true', help='task number', required=False)
    args = parser.parse_args()

    task_key = args.key
    task_num = args.num

    if task_key == None and task_num == False:
        print 'please input at one query parameter'
        parser.print_help()
        sys.exit(-100)

    if task_key != None and task_num != False:
        print 'only one query parameter is allowed'
        parser.print_help()
        sys.exit(-100)

    master_ip       = config.master_ip
    master_rpc_port = config.master_rpc_port
    rpc_addr = "http://" + master_ip + ":" + master_rpc_port
    server = ServerProxy(rpc_addr)

    if task_key != None and len(task_key) != 8:
        print "key format error"
        sys.exit(-100)
    elif task_key != None and len(task_key) == 8:
        ret = server.get_progress(task_key)
        print ret
        ret = int(ret)
        if ret == 100:
            f_list = server.get_target_file(task_key)
            f_list = f_list.replace(' ', '').split('%')
            f_list = filter(lambda a: a != '', f_list)
            print f_list
        sys.exit(ret)

    if task_num == True:
        ret = server.get_blk_num()
        print ret
        sys.exit(ret)




