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
import numpy as np


all_task         = []
pending_task     = []
sim_dur          = 60 * 30
price_per_type   = config.price_per_type
priority         = config.service_type
decay_factor     = config.price_decaying
vm_cost_per_hour = config.vm_cost_per_hour * sim_dur / (60.0 * 60.0)
factor = 1
overall_revenue  = 0
times = 0

max_machine_num = 35
min_machine_num = 10
max_pending_val = 30

grad_w = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
profit = 0
state_v  = 0
state_n  = max_machine_num
state_r  = 1
revenue = 0
dis_b = 0.3


def gen_p():
    return random.randint(1, 1)

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
        value = value + factor * math.pow(decay_factor, t - task.start_time) * \
                price_per_type[task.priority] * (task.est_time / 60.0)
        workload += task.est_time

    return (value, workload)

def sto_grad(num, v, rate):
    num  = float(num)
    v    = float(v)
    rate = float(rate)
    w0 = 1.0
    w1 = num
    w2 = v
    w3 = rate
    w4 = num*num
    w5 = v*v
    w6 = rate*rate
    w7 = num*v
    w8 = num*rate
    w9 = v*rate
    tmp = np.array([w0, w1, w2, w3, w4, w5, w6, w7, w8, w9]) / 1000
    return tmp


def select_best_action(grad_w, state_v):
    action = 0
    max_v  = -10000

    for k in range(min_machine_num, max_machine_num + 1):
        tmp = sto_grad(k, state_v, state_r) * grad_w
        tmp = sum(tmp)
        if tmp > max_v:
            max_v = tmp
            action = k

    a = random.random()
    if a < 1:
        action = random.randint(min_machine_num, max_machine_num)
    return (action, max_v)

t   = 0
a_t = 0
v   = 0
w   = 0

while True:
    times += 1
    if times > 500000:
        break

    cur_time = t
    rate = 1
    state_r = rate
    arrive_rate = rate / 60.0

    (v, w) = feature_extraction(pending_task, t)
    new_state_v = v
    (m_a, m_v)  = select_best_action(grad_w, new_state_v)
    new_state_n = m_a

    dis_f = 1.0 / times
    det = profit + dis_b * m_v -\
            sum(sto_grad(state_n, state_v, state_r) * grad_w)
    #print sum(sto_grad(state_n, state_v, state_r) * grad_w)
    grad_w = grad_w + dis_f * det * sto_grad(state_n, state_v, state_r)
    print grad_w

    state_v  = new_state_v
    state_n   = m_a
    machine_num = m_a

    revenue = 0
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
        #scheduling.schedule_task['hpf'](pending_task)

        if a_t <= t:
            if len(pending_task) == 0:
                a_t = t
            else:
                task = pending_task.pop(0)
                #print 'execute a task:', t
                #print len(pending_task)
                a_t = task.est_time * 1.0 / machine_num + t
                revenue = revenue + factor * price_per_type[task.priority] * (task.est_time / 60.0) \
                                * math.pow(decay_factor, (a_t - task.start_time))
                #print 'estimated time:', a_t

        t = t + 1

    '''
    print '-----------'
    print 'arrival rate:', rate
    print 'machine number:', machine_num
    print 'pending task number', len(pending_task)
    print 'total revenue:', revenue
    print 'total cost:', vm_cost_per_hour * machine_num
    print 'total profit:', revenue - vm_cost_per_hour * machine_num
    '''
    #print len(pending_task)
    #print rate, '\t', machine_num, '\t', v, '\t', w, '\t', len(pending_task), '\t', revenue - vm_cost_per_hour * machine_num
    #print machine_num, '\t', round(10*v), '\t', revenue - vm_cost_per_hour * machine_num
    overall_revenue += (revenue - vm_cost_per_hour * machine_num)
    profit = revenue - vm_cost_per_hour * machine_num
    #print len(pending_task)

#print 'overall revenue:', overall_revenue

for j in range(min_machine_num, max_machine_num + 1):
    for i in range(0, max_pending_val + 1):
        print j, ' ', i, ' ', policy[i][j]

print times
