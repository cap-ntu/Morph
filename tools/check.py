import sys
import random
import time
import signal
import subprocess


f = open('result_key')
lines = f.readlines()
f.close()


for line in lines:
    line = line.replace('\n', '')
    cmd = 'python /home/guanyu/Project/distributed_transcoding/query.py -k ' + line
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    ret = p.returncode

    print ret
