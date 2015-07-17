import sys
import redis
sys.path.append("../.")
import config

list_name = 'vm_list'

redis_ip = config.master_ip
redis_ip = 'localhost'
r = redis.StrictRedis(host=redis_ip, port=6379, db=0)
r.delete(list_name)


f = open('vm.list', 'r')
lines = f.readlines()
for line in lines:
    line = line.strip('\n')
    r.rpush(list_name, line)



print r.lrange(list_name, 0, -1)



