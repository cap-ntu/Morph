import math
import time
import random
import pickle


f = open('arrive_time.pkl', 'r')
arrive_time = pickle.load(f)

duration = 10
start_time = time.time()

while True:
    cur_time = time.time()
    if cur_time - start_time > duration:
        break

    x = a.pop(0)




