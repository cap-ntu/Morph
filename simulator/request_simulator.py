import os
import math
import time
import random
import pickle
from random import choice
from converter import Converter

base_path = '/root/Video/'
video_set = os.listdir(base_path)
service_set = [1, 2, 3]

y_w = [1280, 854, 640, 426]
y_h = [720,  480, 360, 240]

def submit_task():
    while True:
        fname = choice(video_set)
        path = os.path.join(base_path, fname)
        c = Converter()
        info = c.probe(path)
        o_w = info.video.video_width
        o_h = info.video.video_height

        service_type = choice(service_set)
        t_w = -1; t_h = -1; i = 0;
        while i < 4:
            if y_w[i] < o_w and y_h[i] < o_h:
                break
            else:
                i = i + 1

        if i == 4:
            continue

        i = random.randint(i, 3)
        resolution = str(y_w[i]) + 'x' + str(y_h[i])

        cmd = 'python ../submit_task.py -l ' + path + ' -s ' + resolution + ' -p ' + str(service_type) + ' >> task_id '
        os.system(cmd)
        return


f = open('arrive_time.pkl', 'r')
arrive_time = pickle.load(f)

duration = 10*60*60
start_time = time.time()

while True:
    cur_time = time.time()
    if cur_time - start_time > duration:
        break

    if len(arrive_time) == 0:
        break

    x = arrive_time[0]
    if x < cur_time - start_time:
        x = arrive_time.pop(0)
        print x, ' ', cur_time - start_time
        submit_task()
    else:
        time.sleep(5)

