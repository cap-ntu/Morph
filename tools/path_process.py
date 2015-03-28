#!/usr/bin/python

import os
import sys
import time
import subprocess
from converter import Converter

if len(sys.argv) != 3:
    print 'parameter error'
    sys.exit()

print 'file path:', str(sys.argv[1])
print 'target resolution:', str(sys.argv[2])

file_path   = sys.argv[1]
resolution  = sys.argv[2]
c = Converter()

for orig_file in os.listdir(file_path):
    orig_file = os.path.join(file_path, orig_file)
    #print orig_file
    info = c.probe(orig_file)
    (fname, ext) = os.path.splitext(orig_file)
    size = os.stat(orig_file).st_size

    trans = fname + '_' + resolution + ext

    cmd = "ffmpeg -y -i " + orig_file + " -s " + resolution + " -strict -2 " + trans
    #print cmd

    start_time = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    ret = p.returncode

    if ret != 0:
        continue

    elapsed_time = time.time() - start_time
    duration = info.format.duration

    print '------------------'
    print 'file name:', trans
    print 'bitrate (kb/s):', size * 8 / 1024 / duration
    print 'transcoding time:', elapsed_time
    print 'duration:', duration
    print 'speed:', duration / elapsed_time
    print '------------------'





