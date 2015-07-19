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


all_task         = []
pending_task     = []
sim_dur          = 60 * 30
price_per_type   = config.price_per_type
priority         = config.service_type
decay_factor     = config.price_decaying
vm_cost_per_hour = config.vm_cost_per_hour * sim_dur / (60.0 * 60.0)
factor = 0.1
overall_revenue  = 0
times = 0

max_machine_num = 25
min_machine_num = 5
max_pending_val = 50
max_req_rate    = 10
#(0, 0.1 0.2, ...)

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

    return (value, workload, len(task_list))

freq = {}
for i in range(0, max_req_rate + 1):
    freq[i] = {}
    for j in range(0, max_pending_val + 1):
        freq[i][j] = {}
        for k in range(min_machine_num, max_machine_num + 1):
            freq[i][j][k] = 1

policy = {}
for i in range(0, max_req_rate + 1):
    policy[i] = {}
    for j in range(0, max_pending_val + 1):
        policy[i][j] = {}
        for k in range(min_machine_num, max_machine_num + 1):
            policy[i][j][k] = 0.001 * random.random()


def select_best_action(policy, state_r, state_v):
    action = 0
    max_v  = -10000
    p = policy[state_r][state_v]
    for k in p.keys():
        if p[k] > max_v:
            max_v = p[k]
            action = k

    a = random.random()
    if a < 0.3:
        action = random.randint(min_machine_num, max_machine_num)
    return (action, max_v)


profit   = 0
state_r  = 0
state_v  = 0
state_n  = max_machine_num
revenue  = 0
dis_b    = 0.2

t   = 0
a_t = 0
v   = 0

rate_set = [4, 2, 4, 2, 1, 2, 3, 5, 3, 4, 2, 5, 6, 5, 3, 1, 5, 3, 10, 6, 2, 6, 2, 3]

while True:
    times += 1
    if times > 500000:
        break

    cur_time = t
    rate = rate_set[times % 24]
    #machine_num = random.randint(10, 60)
    arrive_rate = rate / 600.0

    (v, _, _) = feature_extraction(pending_task, t)

    new_state_r  = rate
    new_state_v  = round(v * 10)
    (m_a, m_v)   = select_best_action(policy, new_state_r, new_state_v)
    new_state_n  = m_a

    dis_f = 1.0 / freq[state_r][state_v][state_n]
    freq[state_r][state_v][state_n] += 1
    policy[state_r][state_v][state_n] += dis_f * \
            (profit + dis_b * m_v - policy[state_r][state_v][state_n])

    state_r     = new_state_r
    state_n     = m_a
    state_v     = new_state_v
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
    #print profit

#print 'overall revenue:', overall_revenue

for i in range(0, max_req_rate + 1):
    for j in range(0, max_pending_val + 1):
        for k in range(min_machine_num, max_machine_num + 1):
            print i, ' ', j, ' ', k, ' ', policy[i][j][k]

print times
