#-*- coding: utf-8 -*-
#!/usr/bin/python

import paramiko
import threading
import sys
import os
import re


def execute_multi_cmds(ip_list, username, passwd, cmds):
    for ip in ip_list:
        execute_multi_cmd(ip, username, passwd, cmds)


def execute_multi_cmd(ip, username, passwd, cmds):
    lock.acquire()
    print ip
    lock.release()
    str = "-------------------------------\n"
    str +=  "Begin to check machine ...\n"
    str +=  "host ip:" + ip + '\n'

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,passwd,timeout=20)

        for cmd in cmds:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            #str +=  "command:" + cmd +'\n'
            #str +=  "result:" + '\n'
            out = stdout.readlines()
            for o in out:
                str += o


        ssh.close()
        str += "stop checking"
    except:
        str += ip + '\tError\n'

    lock.acquire()
    log.write(str)
    lock.release()



log = open("status.log", "w")
lock = threading.Lock()
lock1 = threading.Lock()


if __name__=='__main__':

    username = "root"
    passwd = ""
    thread_num = 10

    cmds = ['pkill python']
    cmds = ['rm -f /data/worker/*']
    cmds = ['du -sh']
    cmds = ['ps -ef | grep python']
    cmds = ['ps -ef | grep python']
    #cmds = ['nohup  python /root/akilos/worker.py & ']

    f = open("ip.info")
    lines = f.readlines()
    f.close()
    threads = []
    bucket = [ [] for i in range(thread_num) ]

    i = 0
    for line in lines:
        ip = line.replace("\n", "")
        bucket[i%thread_num].append(ip)
        i += 1

    for i in range(0, thread_num):
        ip_list = bucket[i]
        t=threading.Thread(target=execute_multi_cmds, args=(ip_list,username,passwd,cmds))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

    log.close()











