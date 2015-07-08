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
EDF: earliest deadline first
'''
def edf(queue): #0,1,2,...
    f = lambda a, b: a.deadline - b.deadline
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

    v = (pow(price_decaying, task.block_num * seg_trans_time * 1.0 / (machine_num) ) * \
            pow(price_decaying, (t - task.start_time)) * \
            price_per_type[task.priority] * (task.block_num * seg_trans_time / 60.0)) \
                / (1 - pow(price_decaying, task.block_num * seg_trans_time * 1.0 / (machine_num)))
    v = int(v)
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

    h = pow(price_decaying, (t - task.start_time)) * price_per_type[task.priority] \
            * (task.block_num * seg_trans_time / 60.0)
    h = int(h)
    return h

def hvs(queue, t): #N, N-1, N-2, ...
    f = lambda a, b: h_fun(b, t) - h_fun(a, t)
    queue.sort(f)



schedule_task = {
    'fifo':   fifo,
    'edf':    edf,
    'hpf':    hpf,
    'vbs':    vbs,
    'lifo':   lifo,
    'hvs':    hvs,}

