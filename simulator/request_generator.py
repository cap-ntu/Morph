import math
import time
import random
import pickle

t = 0
duration = 100
rate = 1
arrive_time = []

while t < duration:
    t = t + random.expovariate(rate)
    arrive_time.append(t)

f = open('arrive_time.pkl','wb')
pickle.dump(arrive_time, f)
f.close()
