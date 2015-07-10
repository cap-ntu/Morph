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

machine_num = 15
sim_dur = 60 * 60


price_per_type = config.price_per_type

arrive_rate      = 2 / 60.0
decay_factor     = config.price_decaying
vm_cost_per_hour = config.vm_cost_per_hour

class task:
    def __init__(self):
        self.task_id    = 0     #task id
        self.priority   = 0     #task priority
        self.start_time = 0     #the time of adding the transcoding task
        self.est_time   = -1    #the total number of video blocks
        self.end_time   = 0     #the finish time of the task
        self.deadline   = 0     #the deadline for this task
        self.value      = 0     #the estimated value for scheduling

priority = config.service_type
latency  = {}
latency[1] = 0
latency[2] = 0
latency[3] = 0

req_num = {}
req_num[1] = 0
req_num[2] = 0
req_num[3] = 0

task_id = 0

def gen_p():
    #d1
    return random.randint(1, 3)
    #d2
    p = random.randint(1, 100)
    if p <= 10:
        return 1
    if p <= 40:
        return 2
    if p <= 100:
        return 3

if flag == True:
    #generate the tasks
    while t < sim_dur:
        t = t + random.expovariate(arrive_rate)
        x = task()
        x.task_id    = task_id
        x.priority   = gen_p()
        x.start_time = int(t)
        x.est_time   = random.randint(180, 1800) * 1.0
        x.deadline   = int(x.start_time + x.est_time * 3.0)
        all_task.append(x)
        task_id = task_id + 1

    f = open('all_task_sim_sch.pkl','wb')
    pickle.dump(all_task, f)
    f.close()


f = open('all_task_sim_sch.pkl', 'r')
all_task = pickle.load(f)
sum_revenue = 0


t = 0
a_t = 0

#while t < sim_dur + 60*60*3:
while t < sim_dur + 60*60*2:
    while len(all_task) > 0:
        if all_task[0].start_time <= t:
            task = all_task[0]
            all_task.pop(0)
            pending_task.append(task)
        else:
            break


    if algo == 'vbs':
        scheduling.schedule_task[algo](pending_task, t, machine_num)
    elif algo == 'hvs':
        scheduling.schedule_task[algo](pending_task, t, machine_num)
    else:
        scheduling.schedule_task[algo](pending_task)

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
            latency[task.priority] += (t - task.start_time)
            req_num[task.priority] += 1

    t = t + 1

print '-----------'
print algo

print 'pending task number', len(pending_task)
print 'total revenue:', sum_revenue
#print 'total cost:', vm_cost_per_hour * machine_num
#print 'total profit:', sum_revenue - vm_cost_per_hour * machine_num

for key in latency.keys():
    print key, '  ' ,latency[key] * 1.0 / req_num[key]



