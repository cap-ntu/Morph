import sys
import h5py
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
factor           = 0.1 * 1.5
redis_ip         = config.master_ip
redis_ip         = 'localhost'

rate_set = [4, 2, 4, 2, 1, 2, 3, 5, 3, 4, 2, 5, 6, 5, 3, 1, 5, 3, 7, 6, 2, 6, 2, 3]

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
    value = round(value * 10)
    value = int(value)
    return value


r = redis.StrictRedis(host=redis_ip, port=6379, db=0)
r.delete(list_name)

f = h5py.File('policy.mat','r')
data = f.get('policy')
data = np.array(data)
policy = np.transpose(data)
rate_num = 7
val_num  = 15


f = open(list_name, 'r')
lines = f.readlines()
for line in lines:
    line = line.strip('\n')
    r.rpush(list_name, line)

vm_list = r.lrange(list_name, 0, -1)

k = 0
while True:
    if k >= 24:
        break

    task_list = get_pending_task()
    value = feature_extraction(task_list)
    if value > 15:
        value = 15

    cur_rate = rate_set[k]
    index = (cur_rate - 1) * (val_num + 1) + value
    opt_num = policy[index][2]
    opt_num = int(opt_num)
    if opt_num > 23:
        opt_num = 23
    r.set('server_num', opt_num)

    msg = ''
    msg = msg + str(time.time()) + '\n'
    msg = msg + 'cur rate :' + str(cur_rate) + '\n'
    msg = msg + 'cur value:' + str(value) + '\n'
    msg = msg + 'optimal num:' + str(opt_num) + '\n'

    f = open('real_res','a')
    f.write(msg)
    f.close()
    print msg

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

    msg = ''
    msg = msg + str(up_set)
    f = open('real_res','a')
    f.write(msg)
    f.close()
    print msg

    time.sleep(dur)
    k += 1






