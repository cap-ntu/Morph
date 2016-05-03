#!/usr/bin/python

import os
import sys
import time
import random
import subprocess
from converter import Converter

basepath = '/data/video_dataset/'
#new_path = '/data/unused_video_set/'
c = Converter()


for fname in os.listdir(basepath):
    path = os.path.join(basepath, fname)
    if os.path.isdir(path):
        continue

    _, ext = os.path.splitext(path)
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
        #print info.video.video_width, 'x', info.video.video_height
        #print info.video.video_fps
        #print info.video.bitrate
        print info.video.codec
