import math
import time
import random

t = 0
all_task = []
pending_taks = []
finished_tasks = []
machine_num = 10

class task:
    def __init__(self):
        self.priority   = 0     #task priority
        self.start_time = 0     #the time of adding the transcoding task
        self.block_num  = -1    #the total number of video blocks
        self.end_time   = 0     #the finish time of the task
        self.deadline   = 0     #the deadline for this task
        self.value      = 0     #the estimated value for scheduling

while t < 60:
    t = t + random.expovariate(1.0)
    x = task()
    x.priority = random.randint(1, 3)
    x.start_time = t
    x.block_num = random.randint(5, 20)
    all_task.append(x)

t = 0
while t < 60:
    pending_task = all_task
    pending_task = [x for x in pending_task if x.start_time <= t]



    print len(pending_task)
    time.sleep(1)
    t = t + 1
