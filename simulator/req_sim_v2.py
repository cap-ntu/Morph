import os
import time
import pickle

class task:
    def __init__(self):
        self.priority   = 0     #task priority
        self.start_time = 0     #the time of adding the transcoding task
        self.tgt_res    = 0     #resolution
        self.video_name = ''    #video name


def submit_task(task):
    cmd = 'python ../submit_task.py -l ' + task.video_name + ' -s ' + \
            task.tgt_res + ' -p ' + str(task.priority)
    print cmd
    print 'start time:', task.start_time
    os.system(cmd)
    return


f = open('sim_v3.pkl', 'r')
all_task = pickle.load(f)
f.close()

#duration = 60*180
start_time = time.time()

while True:
    cur_time = time.time()
    #if cur_time - start_time > duration:
    #    break

    if len(all_task) == 0:
        break

    if all_task[0].start_time <= (cur_time - start_time):
        task = all_task[0]
        all_task.pop(0)
        submit_task(task)
    else:
        time.sleep(3)



