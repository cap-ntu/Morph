
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
    f = lambda a, b: a.priority - b.priority
    queue.sort(f)

'''
VBS: value-based task scheduling
'''
def vbs(queue):
    f = lambda a, b: a.priority - b.priority
    queue.sort(f)

schedule_task = {
    'fifo': fifo,
    'edf':  edf,
    'hpf':  hpf,
    'vbs':  vbs,}


