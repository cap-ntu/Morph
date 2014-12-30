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
        sys.exit()

    if task_key != None and task_num != False:
        print 'only one query parameter is allowed'
        parser.print_help()
        sys.exit()

    master_ip       = config.master_ip
    master_rpc_port = config.master_rpc_port
    rpc_addr = "http://" + master_ip + ":" + master_rpc_port
    server = ServerProxy(rpc_addr)

    if task_key != None and len(task_key) != 8:
        print "key format error"
        sys.exit()
    elif task_key != None and len(task_key) == 8:
        ret = server.get_progress(task_key)
        print ret

    if task_num == True:
        ret = server.get_blk_num()
        print ret










