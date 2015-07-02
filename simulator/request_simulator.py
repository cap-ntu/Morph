import math
import time
import random
import pickle


f = open('arrive_time.pkl', 'r')
arrive_time = pickle.load(f)

duration = 100
start_time = time.time()

while True:
    cur_time = time.time()
    if cur_time - start_time > duration:
        break

    if len(arrive_time) == 0:
        break

    x = arrive_time[0]
    if x < cur_time - start_time:
        x = arrive_time.pop(0)
        print x, ' ', cur_time - start_time
    else:
        time.sleep(0.5)

