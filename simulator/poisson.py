import math
import random

i = 0
while i < 60:
    i = i + random.expovariate(1.0/20)
    print i
