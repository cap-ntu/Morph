#!/usr/bin/python

import os
import sys
import time
import random
import subprocess
from converter import Converter

if len(sys.argv) != 3:
    print 'parameter error'
    sys.exit()


print 'video file name:', str(sys.argv[1])
print 'target resolution:', str(sys.argv[2])

c = Converter()

orig_file   = sys.argv[1]
resolution  = sys.argv[2]
times     = 50

(fname, ext) = os.path.splitext(orig_file)
info = c.probe(orig_file)
v_dur = int(info.format.duration)

for i in range(1, times):
    start = random.randint(0, v_dur)
    duration = random.randint(5*60, 30*60)
    if start + duration >= v_dur:
        continue

    m, s = divmod(start, 60)
    h, m = divmod(m, 60)
    start = "%02d:%02d:%02d" % (h, m, s)

    m, s = divmod(duration, 60)
    h, m = divmod(m, 60)
    length = "%02d:%02d:%02d" % (h, m, s)

    output = fname + '_' + str(m) + 'min' + ext
    trans  = fname + '_' + str(m) + 'min' + '_' + resolution + ext

    cmd = "ffmpeg -y -i " + orig_file + " -ss " + start + " -t " + length + \
            " -vcodec copy -acodec copy " + output
    #print cmd

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    ret = p.returncode

    size = os.stat(output).st_size

    cmd = "ffmpeg -y -i " + output + " -s " + resolution + " -strict -2 " + trans
    #print cmd

    start_time = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    ret = p.returncode
    elapsed_time = time.time() - start_time

    if ret != 0:
        continue

    print '------------------'
    print 'file name:', trans
    print 'duration:', duration
    print 'bitrate (b/s):', size * 8 / 1024 / duration
    print 'transcoding time:', elapsed_time
    #print 'speed:', duration / elapsed_time
    print '------------------'





