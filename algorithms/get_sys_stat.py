import sys
sys.path.append("../.")
import time
import config
import sqlite3 as lite


def get_vm_info():
    try:
        path = '../' + config.db_name
        con = lite.connect(path)
        cur = con.cursor()
        sql_cmd = "SELECT * FROM server_info WHERE id = 'current'"
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        row = rows[0]
        serv_num = row[0]
        ip_list = row[1]
        return (serv_num, ip_list)

    except lite.Error, e:
        print "Error %s:" % e.args[0]

    finally:
        con.close()

def get_pending_task():
    try:
        path = '../' + config.db_name
        con = lite.connect(path)
        cur = con.cursor()
        sql_cmd = 'SELECT * FROM task_info WHERE task_ongoing = 0'
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        return rows
        #for row in rows:
        #    if row != None:
        #        print row

    except lite.Error, e:
        print "Error %s:" % e.args[0]

    finally:
        con.close()

def feature_extraction(task_list):
    value = 0
    workload = 0
    cur_time = time.time()
    for task in task_list:
        value = value + math.pow( , cur_time - task[1])
        workload += task[4]

    return (value, workload)


'''
(serv_num, ip_list) = get_vm_info()
print serv_num
print ip_list
'''

task_list = get_pending_task()
feature = feature_extraction(task_list)
feature = ()

