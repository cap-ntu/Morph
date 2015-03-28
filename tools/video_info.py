#!/usr/bin/python

import os
import sys
import time
import random
import subprocess
from converter import Converter

basepath = '/home/guanyu/Data/1280x720'
#new_path = '/home/guanyu/Data/1280x720/'
c = Converter()


for fname in os.listdir(basepath):
    path = os.path.join(basepath, fname)
    if os.path.isdir(path):
        continue

    _, ext = os.path.splitext(path)
    if ext == '.mp4':
        info = c.probe(path)

        if info.video.video_width == 1280:
            #print info.video.video_width, 'x', info.video.video_height
            print info.format.duration
            #os.rename(path, new_path + fname)
