'''
The implemented task scheduling algorithms
'''

from math import pow
import sys
import time
sys.path.append("../.")
import config

'''
FIFO: first in first out
'''
def fifo(queue): #0,1,2,...
    f = lambda a, b: a.start_time - b.start_time
    queue.sort(f)

'''
Get the deadline of a transcoding task
'''
def get_deadline(task):
    d = int(task.start_time + task.est_time * 3.0)
    return d

'''
EDF: earliest deadline first
'''
def edf(queue): #0,1,2,...
    f = lambda a, b: get_deadline(a) - get_deadline(b)
    queue.sort(f)

'''
HPF: highest priority first
'''
def hpf(queue): #0,1,2,...
    f = lambda a, b: a.priority - b.priority
    queue.sort(f)

'''
valuation function
'''
def v_fun(task, t, machine_num):
    price_decaying = config.price_decaying
    seg_trans_time = config.equal_trans_dur
    price_per_type = config.price_per_type

    v = (pow(price_decaying, task.est_time * 1.0 / machine_num) * \
            pow(price_decaying, t - task.start_time) * \
            price_per_type[task.priority] * (task.est_time / 60.0)) \
                / (1 - pow(price_decaying, task.est_time * 1.0 / machine_num))
    v = int(v*10000)
    return v

'''
VBS: value-based task scheduling
'''
def vbs(queue, t, machine_num): #N, N-1, N-2,...
    f = lambda a, b: v_fun(b, t, machine_num) - v_fun(a, t, machine_num)
    queue.sort(f)

'''
lifo: last in first out
'''
def lifo(queue): #N, N-1, N-2,...
    f = lambda a, b: b.start_time - a.start_time
    queue.sort(f)

'''
hvs: highest value first
'''
def h_fun(task, t):
    price_decaying = config.price_decaying
    seg_trans_time = config.equal_trans_dur
    price_per_type = config.price_per_type

    h = pow(price_decaying, t - task.start_time) * price_per_type[task.priority] \
            * (task.est_time / 60.0)
    h = int(h*10000)
    return h

def hvs(queue, t, machine_num): #N, N-1, N-2, ...
    f = lambda a, b: h_fun(b, t) - h_fun(a, t)
    queue.sort(f)


#select the task scheduling algorithm by configuring the config.py
schedule_task = {
    'fifo':   fifo,
    'edf':    edf,
    'hpf':    hpf,
    'vbs':    vbs,
    'lifo':   lifo,
    'hvs':    hvs,}

