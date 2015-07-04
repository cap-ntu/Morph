from math import pow
import time

'''
FIFO: first in first out
'''
def fifo(queue):
    f = lambda a, b: a.start_time - b.start_time
    queue.sort(f)

'''
EDF: earliest deadline first
'''
def edf(queue):
    f = lambda a, b: a.deadline - b.deadline
    queue.sort(f)

'''
HPF: highest priority first
'''
def hpf(queue):
    f = lambda a, b: b.priority - a.priority
    queue.sort(f)

'''
valuation function
'''
def v_fun(task, t):
    price_decaying = 0.999
    seg_trans_time = 60.0
    machine_num = 10
    v = (pow(price_decaying, task.block_num * seg_trans_time * 1.0 / (machine_num) ) * \
            pow(price_decaying, (t - task.start_time)) * \
            task.priority * task.block_num) / (1 - pow(price_decaying, task.block_num * seg_trans_time * 1.0 / (machine_num)))
    v = int(v)
    return v

'''
VBS: value-based task scheduling
'''
def vbs(queue, t):
    f = lambda a, b: v_fun(b, t) - v_fun(a, t)
    queue.sort(f)

'''
lifo: last in first out
'''
def lifo(queue):
    f = lambda a, b: b.start_time - a.start_time
    queue.sort(f)

schedule_task = {
    'fifo': fifo,
    'edf':  edf,
    'hpf':  hpf,
    'vbs':  vbs,}


