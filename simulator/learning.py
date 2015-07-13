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

aa = [197, 140, 93, 45, 63, 31, 66, 70, 89, 173, 151, 228, 243, 255, 272, 234, 227, 225, 300, 301, 343, 292, 261, 267]

all_task = []
pending_task = []
sim_dur = 60 * 60
price_per_type   = config.price_per_type
priority         = config.service_type
decay_factor     = config.price_decaying
vm_cost_per_hour = config.vm_cost_per_hour
factor = 4
overall_revenue  = 0
times = 0

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

def feature_extraction(task_list, t):
    value = 0
    workload = 0
    for task in task_list:
        value = value + math.pow(decay_factor, t - task.start_time) * \
                price_per_type[task.priority] * (task.est_time / 60.0)
        workload += task.est_time

    return (value, workload)


class system_state:
    pass

policy = {}
for i in range(1, 13):
    policy[i] = {}
    for j in range(1, 31):
        policy[i][j] = 0

def select_best_action(policy, state_rate):
    action = 0
    max_v  = -10000
    p = policy[state_rate]
    for k in p.keys():
        if p[k] > max_v:
            max_v = p[k]
            action = k
    return (action, max_v)


state_rate  = 1
state_num   = 1
sum_revenue = 0

dis_f = 0.1
dis_b = 0.9

t = 0
a_t = 0

while True:
    times += 1
    if times > 1000:
        break

    cur_time = t
    rate = aa[times % 24]
    #machine_num = random.randint(1, 30)
    arrive_rate = rate / 60.0

    new_state_rate = int(rate * 10)
    new_state_num  = machine_num

    (action, m_v)  = select_best_action(policy, state_rate)

    policy[state_rate][state_num] += dis_f * \
            (sum_revenue - dis_b * m_v - policy[state_rate][state_num])

    state_rate = new_state_rate
    state_num  = action


    sum_revenue = 0
    while True:
        t = t + random.expovariate(arrive_rate)
        if t >= cur_time + sim_dur:
            break

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
                sum_revenue = sum_revenue + factor * price_per_type[task.priority] * (task.est_time / 60.0) \
                                * math.pow(decay_factor, (a_t - task.start_time))
                #print 'estimated time:', a_t

        t = t + 1

    (v, w) = feature_extraction(pending_task, t)
    '''
    print '-----------'
    print 'arrival rate:', rate
    print 'machine number:', machine_num
    print 'pending task number', len(pending_task)
    print 'total revenue:', sum_revenue
    print 'total cost:', vm_cost_per_hour * machine_num
    print 'total profit:', sum_revenue - vm_cost_per_hour * machine_num
    '''
    print rate, '\t', machine_num, '\t', v, '\t', w, '\t', len(pending_task), '\t', sum_revenue - vm_cost_per_hour * machine_num
    overall_revenue += (sum_revenue - vm_cost_per_hour * machine_num)

print 'overall revenue:', overall_revenue



