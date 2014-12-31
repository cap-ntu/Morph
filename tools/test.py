import sys
import random
import time
import signal
import subprocess

flag = True

def signal_handler(signal, frame):
    global flag
    flag = False
    print('stop testing')

signal.signal(signal.SIGINT, signal_handler)

f = open('video.list')
lines = f.readlines()
f.close()

video_list = []

for line in lines:
    line = line.replace('\n', '')
    video_list.append(line)

while flag:
    cmd = 'python /home/guanyu/Project/distributed_transcoding/query.py -n'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    ret = p.returncode

    if ret > 50:
        time.sleep(10)
        continue
    else:
        video = random.choice(video_list)
        cmd = 'python /home/guanyu/Project/distributed_transcoding/client.py -i ' + \
                video + ' ' + '-s 640x360  426x240'
        print cmd
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        ret = p.returncode
        if ret == 0:
            key = stdout.replace('\n', '')
            print key
            time.sleep(120)



