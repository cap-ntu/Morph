#!/usr/bin/python

import os
import sys
import time
import random
import subprocess
from converter import Converter

basepath = '/data/video_dataset/'
c = Converter()

f = open('trans_res.dat','w')

y_w = [1280, 854, 640, 426]
y_h = [720,  480, 360, 240]

for fname in os.listdir(basepath):
    path = os.path.join(basepath, fname)
    if os.path.isdir(path):
        continue

    name, ext = os.path.splitext(path)
    if ext == '.mp4':
        info = c.probe(path)

        #if info.video.video_width == 1280:
            #print info.video.video_width, 'x', info.video.video_height
        #dur = info.format.duration
        #print dur/60.0
        '''
        if dur > 2*60 and dur < 60*60*1.5:
            os.rename(path, new_path + fname)
            print dur/60.0
        '''
        o_w = info.video.video_width
        o_h = info.video.video_height
        o_f = info.video.video_fps
        o_b = info.video.bitrate
        o_c = info.video.codec
        o_d = info.format.duration

        if o_d > 60*3:
            continue

        for i in range(4):
            if o_w > y_w[i] and o_h > y_h[i]:

                resolution = str(y_w[i]) + 'x' + str(y_h[i])

                trans = name + '_' + resolution + ext

                cmd = "ffmpeg -y -i " + path + " -s " + resolution + " -strict -2 " + trans
                print cmd

                start_time = time.time()
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                stdout, stderr = p.communicate()
                ret = p.returncode
                elapsed_time = time.time() - start_time

                res = fname + ' '+ str(o_d) + ' ' + str(o_w) + ' ' + str(o_h) + ' ' + str(o_f) + \
                        ' ' + str(o_b) + ' '+ o_c + ' ' + resolution + ' ' + str(elapsed_time) + '\n'
                print res,
                f.write(res)
                f.flush()

f.close()





