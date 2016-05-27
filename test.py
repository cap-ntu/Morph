'''
Author: Guanyu Gao
Email:  guanyugao@gmail.com
Description:
Resource management for controlling the transcoding workers
'''

import sys
import time
import config
import MySQLdb
from sys_info import *


sched_feq = 60
list_name = 'vm.list'
ip        = config.mysql_ip
passwd    = config.mysql_password
user_name = config.mysql_user_name
db_name   = config.mysql_db_name


'''
get the current number of pending transcoding tasks
'''
def get_pending_task():
    try:
        con = MySQLdb.connect(ip, user_name, passwd, db_name)
        cur = con.cursor()
        sql_cmd = 'SELECT * FROM task_info WHERE task_ongoing = 1'
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        con.close()
        return rows
    except Exception, e:
        print str(e)
        return -1

def db_update_worker_state(host_name, state):
    try:
        con = MySQLdb.connect(ip, user_name, passwd, db_name)
        cur = con.cursor()
        sql_cmd = "UPDATE server_info SET state = %d WHERE id = '%s'" \
                    % (state, host_name)
        print sql_cmd
        cur.execute(sql_cmd)
        con.commit()
        con.close()
        return 0
    except:
        return -1

'''
to estimate the workload of the pending tasks using whatever method
'''
def feature_extraction(task_list):
    return len(task_list)

'''
determine the optimal number of instances using whatever method
'''
def policy(workload):
    MIN_NUM = 1
    MAX_NUM = 100
    if workload <= 0:
        return MIN_NUM
    else:
        return MAX_NUM


if __name__ == '__main__':

    vm_list = []
    f = open(list_name, 'r')
    lines = f.readlines()
    for line in lines:
        line = line.strip('\n')
        line = line.replace(" ", "").lower()
        vm_list.append(line)

    capacity = len(vm_list)

    while True:
        #get the pending tasks
        task_list = get_pending_task()
        value = feature_extraction(task_list)
        opt_num = policy(value)
        if opt_num > capacity:
            opt_num = capacity

        up_set   = []
        up_num   = 0
        down_set = []
        down_num = 0

        for vm in vm_list:
            ret = db_get_worker_state(vm)
            if ret == -1:
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
                db_update_worker_state(vm, 1)
        elif opt_num < up_num:
            for i in range(0, up_num - opt_num):
                vm = up_set.pop(0)
                db_update_worker_state(vm, 0)

        time.sleep(sched_feq)


