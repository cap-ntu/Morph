import math
import time
import random

t = 0
all_task = []
pending_taks = []
finished_tasks = []
machine_num = 10
duration = 100
arrive_rate = 1

decay_factor = 0.99

class task:
    def __init__(self):
        self.priority   = 0     #task priority
        self.start_time = 0     #the time of adding the transcoding task
        self.block_num  = -1    #the total number of video blocks
        self.end_time   = 0     #the finish time of the task
        self.deadline   = 0     #the deadline for this task
        self.value      = 0     #the estimated value for scheduling

def sched_algo(pending_task):


#generate the tasks
while t < duration:
    t = t + random.expovariate(arrive_rate)
    x = task()
    x.priority = random.randint(1, 3)
    x.start_time = t
    x.block_num = random.randint(5, 20)
    all_task.append(x)


t = 0
next_a_t = 0

while t < duration:
    pending_task = [x for x in all_task if x.start_time <= t]

    print 'current time:', t, ' ',
    for x in pending_task:
        print x.start_time, ' ',
    print ' '

    t = t + 1
    time.sleep(2)


