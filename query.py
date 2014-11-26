import os
import sys
import config
import argparse
from common import *
from xmlrpclib import ServerProxy

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', help='task key', required=True)
    args = parser.parse_args()

    task_key = args.key
    if len(task_key) != 8:
        print "key format error"
        sys.exit()

    master_ip       = config.master_ip
    master_rpc_port = config.master_rpc_port
    rpc_addr = "http://" + master_ip + ":" + master_rpc_port
    server = ServerProxy(rpc_addr)

    ret = server.get_progress(task_key)
    print ret




