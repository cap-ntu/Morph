import sys
import random
import time
import signal
import subprocess


f = open('task_key')
lines = f.readlines()
f.close()


for line in lines:
    line = line.replace('\n', '')
    cmd = 'python /root/akilos/get_progress.py -k ' + line
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    ret = p.returncode
    #if ret > 100:
    #   print line 

    print ret
