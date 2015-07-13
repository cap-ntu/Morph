import os
import math
import time
import random
import pickle
from random import choice
from converter import Converter

base_path = '/data/video_dataset/'
video_set = os.listdir(base_path)
sim_dur = 60 * 180
arrive_rate = 1.0 / 60.0

y_w = [854, 640, 426]
y_h = [480, 360, 240]

class task:
    def __init__(self):
        self.priority   = 0     #task priority
        self.start_time = 0     #the time of adding the transcoding task
        self.tgt_res    = 0     #resolution
        self.video_name = ''    #video name

def gen_p():
    #d1
    return random.randint(1, 3)
    #d2
    p = random.randint(1, 100)
    if p <= 10:
        return 1
    if p <= 40:
        return 2
    if p <= 100:
        return 3

t = 0
all_task = []
while t < sim_dur:
    t = t + random.expovariate(arrive_rate)
    x = task()
    x.priority   = gen_p()
    x.start_time = int(t)
    fname = choice(video_set)
    path  = os.path.join(base_path, fname)
    x.video_name = path

    c = Converter()
    info = c.probe(path)
    o_w = info.video.video_width
    o_h = info.video.video_height

    t_w = -1; t_h = -1; i = 0;
    while i < 3:
        if y_w[i] < o_w and y_h[i] < o_h:
            break
        else:
            i = i + 1

    if i == 3:
        i = 2

    i = random.randint(i, 2)
    resolution = str(y_w[i]) + 'x' + str(y_h[i])
    x.tgt_res  = resolution
    all_task.append(x)


f = open('sim_v2.pkl','wb')
pickle.dump(all_task, f)
f.close()



