import redis
import time

list_name = 'vm.list'
redis_ip  = 'localhost'
r = redis.StrictRedis(host=redis_ip, port=6379, db=0)
#print r.keys()

'''
f = open(list_name, 'r')
lines = f.readlines()
for line in lines:
    line = line.strip('\n')
    r.set(line, 1)
'''

f = open(list_name, 'r')
lines = f.readlines()
for line in lines:
    line = line.strip('\n')
    last_time = r.get(line + '_time')
    cur_time  = time.time()
    print (cur_time - float(last_time)) / 60.0

'''
f = open(list_name, 'r')
lines = f.readlines()
for line in lines:
    line = line.strip('\n')
    print r.get(line)
'''
