import sys
import math
import time
import redis
sys.path.append("../.")
import config
import numpy as np
import sqlite3 as lite

list_name        = 'vm.list'
dur              = 60 * 30
price_per_type   = config.price_per_type
priority         = config.service_type
decay_factor     = config.price_decaying
vm_cost_per_hour = config.vm_cost_per_hour * dur / (60.0 * 60.0)
factor           = 1
redis_ip         = config.master_ip
redis_ip         = 'localhost'

def get_pending_task():
    con  = None
    rows = None
    try:
        path = '../' + config.db_name
        con = lite.connect(path)
        cur = con.cursor()
        sql_cmd = 'SELECT * FROM task_info WHERE task_ongoing = 1'
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        #for row in rows:
        #    if row != None:
        #        print row

    except lite.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        con.close()
        return rows

def feature_extraction(task_list):
    value = 0
    cur_time = time.time()
    for task in task_list:
        value = value + factor * math.pow(decay_factor, cur_time - task[1]) * \
                price_per_type[task[4]] * (task[5] / 60.0)
    value = round(value)
    value = int(value)
    print value
    return value


r = redis.StrictRedis(host=redis_ip, port=6379, db=0)
r.delete(list_name)
#policy = np.loadtxt('policy.dat')
policy = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]

f = open(list_name, 'r')
lines = f.readlines()
for line in lines:
    line = line.strip('\n')
    r.rpush(list_name, line)

vm_list = r.lrange(list_name, 0, -1)
#for vm in vm_list:
#    r.set(vm, 0)

times = 0
while True:
    times += 1
    if times > 10:
        break

    task_list = get_pending_task()
    value = feature_extraction(task_list)
    if value > len(policy) - 1:
        print 'out of scale'
        sys.exit()
    opt_num = policy[value]
    opt_num = int(opt_num)
    print 'optimal num:', opt_num

    up_set   = []
    up_num   = 0
    down_set = []
    down_num = 0

    for vm in vm_list:
        ret = r.get(vm)
        if ret == None:
            print 'vm does not exist'
            continue
        elif int(ret) == 0:
            down_num += 1
            down_set.append(vm)
        elif int(ret) == 1:
            up_num += 1
            up_set.append(vm)

    if opt_num == up_num:
        pass
    elif opt_num > up_num:
        for i in range(0, opt_num - up_num):
            vm = down_set.pop(0)
            r.set(vm, 1)
    elif opt_num < up_num:
        for i in range(0, up_num - opt_num):
            vm = up_set.pop(0)
            r.set(vm, 0)

    time.sleep(dur)






