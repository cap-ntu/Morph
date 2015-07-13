import random
import pickle

n = 0
max_num = 50
arrive_rate = 3.0 / 60.0

class task:
    def __init__(self):
        self.priority   = 0     #task priority
        self.start_time = 0     #the time of adding the transcoding task
        self.tgt_res    = 0     #resolution
        self.video_name = ''    #video name


f = open('sim_v2.pkl', 'r')
all_task = pickle.load(f)
f.close()


t = 0
new_task = []
while n < max_num:
    t = t + random.expovariate(arrive_rate)
    x = all_task.pop(0)
    x.start_time = t
    new_task.append(x)
    n = n + 1


f = open('sim_v3.pkl','wb')
pickle.dump(new_task, f)
f.close()



