import os
import sys
import math
import time
import random
sys.path.append("../algorithms")
import scheduling

t = 0
all_task = []
pending_task = []
finished_tasks = []
machine_num = 10
duration = 60 * 100
arrive_rate = 1.2 / (75.0)
seg_trans_time = 60.0
decay_factor = 0.99

class task:
    def __init__(self):
        self.priority   = 0     #task priority
        self.start_time = 0     #the time of adding the transcoding task
        self.block_num  = -1    #the total number of video blocks
        self.end_time   = 0     #the finish time of the task
        self.deadline   = 0     #the deadline for this task
        self.value      = 0     #the estimated value for scheduling


#generate the tasks
while t < duration:
    t = t + random.expovariate(arrive_rate)
    x = task()
    x.priority = random.randint(1, 3)
    x.start_time = int(t)
    x.block_num = random.randint(4, 20)
    all_task.append(x)


print len(all_task)

t = 0
a_t = 0

while t < duration:

    for x in all_task:
        if x.start_time <= t:
            task = x
            all_task.remove(x)
            pending_task.append(task)

    scheduling.fifo(pending_task)

    '''
    print 'current time:', t, ':',
    for x in pending_task:
        print x.start_time, ' ',
    print ' '
    '''

    if a_t <= t:
        if len(pending_task) == 0:
            a_t = t
        else:
            task = pending_task.pop(0)
            #print 'execute a task:', t
            print len(pending_task)
            a_t = task.block_num * seg_trans_time * 1.0 / machine_num + t
            #print 'estimated time:', a_t

    t = t + 1

