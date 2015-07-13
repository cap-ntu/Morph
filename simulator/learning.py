import os
import sys
import math
import time
import random
import pickle
sys.path.append("../.")
import config
sys.path.append("../algorithms")
import scheduling
import trans_time


all_task = []
pending_task = []
sim_dur = 60 * 60
price_per_type   = config.price_per_type
priority         = config.service_type
decay_factor     = config.price_decaying
vm_cost_per_hour = config.vm_cost_per_hour


def gen_p():
    return random.randint(1, 3)

class trans_task:
    def __init__(self):
        self.priority   = 0     #task priority
        self.start_time = 0     #the time of adding the transcoding task
        self.est_time   = -1    #the total number of video blocks
        self.end_time   = 0     #the finish time of the task
        self.deadline   = 0     #the deadline for this task
        self.value      = 0     #the estimated value for scheduling


t = 0
a_t = 0
while True:

    cur_time = t
    rate = random.uniform(0, 3)
    machine_num = random.randint(10, 30)
    arrive_rate = rate / 60.0

    sum_revenue = 0
    while t < cur_time + sim_dur:
        t = t + random.expovariate(arrive_rate)
        x = trans_task()
        x.priority   = gen_p()
        x.start_time = int(t)
        #x.est_time  = random.randint(180, 1800) * 1.0
        x.est_time   = random.choice(trans_time.a)
        all_task.append(x)

    t = cur_time
    while t - cur_time < sim_dur:
        while len(all_task) > 0:
            if all_task[0].start_time <= t:
                task = all_task[0]
                all_task.pop(0)
                pending_task.append(task)
            else:
                break

        scheduling.schedule_task['vbs'](pending_task, t, machine_num)

        if a_t <= t:
            if len(pending_task) == 0:
                a_t = t
            else:
                task = pending_task.pop(0)
                #print 'execute a task:', t
                #print len(pending_task)
                a_t = task.est_time * 1.0 / machine_num + t
                sum_revenue = sum_revenue + price_per_type[task.priority] * (task.est_time / 60.0) \
                                * math.pow(decay_factor, (a_t - task.start_time))
                #print 'estimated time:', a_t

        t = t + 1

    print '-----------'
    print 'arrival rate:', arrive_rate
    print 'pending task number', len(pending_task)
    print 'total revenue:', sum_revenue
    print 'total cost:', vm_cost_per_hour * machine_num
    print 'total profit:', sum_revenue - vm_cost_per_hour * machine_num




