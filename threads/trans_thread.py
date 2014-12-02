import os
import sys
import time
import signal
import threading
import subprocess

ts_num = 0
path = sys.argv[1]
resolution = sys.argv[2]
all_files  = os.listdir(path)
start_time = time.time()

class trans_thread(threading.Thread):

    def __init__(self, lock, index):
        threading.Thread.__init__(self)
        self.lock   = lock
        self.index  = index

    def run(self):

        global path
        global ts_num
        global resolution
        global all_files
        global start_time

        while True:
            self.lock.acquire()
            try:
                file_name = all_files.pop()
            except:
                self.lock.release()
                break
            self.lock.release()

            input_file = os.path.join(path, file_name)
            name, suffix = os.path.splitext(input_file)
            if suffix != ".ts" or resolution in name:
                continue

            output_file = name + "_" + resolution + ".ts"

            cmd = "ffmpeg -y -i " + input_file + " -s " + \
                    resolution + " " + output_file
            print cmd

            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            #for line in p.stdout.readlines():
            #    print line,
            retval = p.wait()


            self.lock.acquire()
            ts_num = ts_num + 1
            self.lock.release()

            exec_time = time.time() - start_time
            ave_speed = exec_time / ts_num
            print "average speed is ", ave_speed


lock = threading.Lock()
thread_num = 2
threads = []


try:
    for i in range(0, thread_num):
        t = trans_thread(lock, i)
        t.start()
        threads.append(t)
except:
    print "Error: unable to start thread"

for t in threads:
    t.join()



