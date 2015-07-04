import os
import sys
import math
import time
import math
import random
import pickle
sys.path.append("../algorithms")
import scheduling

flag = False

if len(sys.argv) != 3:
    print 'argument error'
    sys.exit()

if sys.argv[1] == '1':
    flag = True

algo = sys.argv[2]


t = 0
all_task = []
pending_task = []
finished_tasks = []
machine_num = 10
duration = 60 * 500
arrive_rate = 1 / (60.0*4)
seg_trans_time = 60.0
decay_factor = 0.999

class task:
    def __init__(self):
        self.task_id    = 0
        self.priority   = 0     #task priority
        self.start_time = 0     #the time of adding the transcoding task
        self.block_num  = -1    #the total number of video blocks
        self.end_time   = 0     #the finish time of the task
        self.deadline   = 0     #the deadline for this task
        self.value      = 0     #the estimated value for scheduling

id = 0
if flag == True:
    #generate the tasks
    while t < duration:
        t = t + random.expovariate(arrive_rate)
        x = task()
        x.task_id = id
        id = id + 1
        x.priority = random.randint(1, 3)
        x.start_time = int(t)
        x.block_num = random.randint(4, 90)
        x.deadline  = int(x.start_time + x.block_num * seg_trans_time * 3.0 / machine_num)
        all_task.append(x)

    f = open('all_task.pkl','wb')
    pickle.dump(all_task, f)
    f.close()

f = open('all_task.pkl', 'r')
all_task = pickle.load(f)

sum_revenue = 0

#print len(all_task)

t = 0
a_t = 0

while t < duration:
    while len(all_task) > 0:
        if all_task[0].start_time <= t:
            task = all_task[0]
            all_task.pop(0)
            pending_task.append(task)
        else:
            break

    #scheduling.hpf(pending_task)
    #scheduling.fifo(pending_task)
    #scheduling.edf(pending_task)
    #scheduling.vbs(pending_task, t)

    if algo == 'vbs':
        scheduling.schedule_task[algo](pending_task, t)
    else:
        scheduling.schedule_task[algo](pending_task)


    if a_t <= t:
        if len(pending_task) == 0:
            a_t = t
        else:
            task = pending_task.pop(0)
            #print 'execute a task:', t
            #print len(pending_task)
            a_t = task.block_num * seg_trans_time * 1.0 / machine_num + t
            sum_revenue = sum_revenue + task.priority * task.block_num * 1.0 * math.pow(decay_factor, (a_t - task.start_time))
            #print 'estimated time:', a_t

    t = t + 1

print sum_revenue
