'''
Author: Guanyu Gao
Email:  guanyugao@gmail.com
Description: the interface for accessing the Mysql database.
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import config
import MySQLdb

ip        = config.mysql_ip
passwd    = config.mysql_password
user_name = config.mysql_user_name
db_name   = config.mysql_db_name

def init_db():
    try:
        con = MySQLdb.connect(ip, user_name, passwd, db_name)
        cur = con.cursor()
        cur.execute("create table if not exists task_info(id TEXT, submit_time REAL, start_time REAL, \
                finish_time REAL, service_type INTEGER, trans_time REAL, task_ongoing INTEGER)")
        con.commit()

        cur.execute("create table if not exists server_info(id TEXT NOT NULL PRIMARY KEY, last_time REAL, state INTEGER)")
        con.commit()

        con.close()
        return 0
    except:
        con.rollback()
        return -1

def db_insert_task_info(task_id, service_type):
    try:
        con = MySQLdb.connect(ip, user_name, passwd, db_name)
        cur = con.cursor()
        cur_time = time.time()
        sql_cmd = "INSERT INTO task_info VALUES('%s', %f, -1, -1, %d, -1, 1)" \
                    % (task_id, cur_time, service_type)
        cur.execute(sql_cmd)
        con.commit()
        con.close()
        return 0
    except:
        con.rollback()
        return -1

def db_update_finish_time(task_id, result):
    try:
        con = MySQLdb.connect(ip, user_name, passwd, db_name)
        cur = con.cursor()
        cur_time = time.time()
        sql_cmd = "UPDATE task_info SET finish_time = %f, task_ongoing = %d WHERE id = '%s'" \
                    % (cur_time, result, task_id)
        print sql_cmd
        cur.execute(sql_cmd)
        con.commit()
        con.close()
        return 0
    except:
        con.rollback()
        return -1

def db_update_start_time(task_id):
    try:
        con = MySQLdb.connect(ip, user_name, passwd, db_name)
        cur = con.cursor()
        cur_time = time.time()
        sql_cmd = "UPDATE task_info SET start_time = %f WHERE id = '%s'" \
                    % (cur_time, task_id)
        print sql_cmd
        cur.execute(sql_cmd)
        con.commit()
        con.close()
        return 0
    except:
        con.rollback()
        return -1


def db_update_trans_time(task_id, trans_time):
    try:
        con = MySQLdb.connect(ip, user_name, passwd, db_name)
        cur = con.cursor()
        sql_cmd = "UPDATE task_info SET trans_time = %f WHERE id = '%s'" \
                    % (trans_time, task_id)
        print sql_cmd
        cur.execute(sql_cmd)
        con.commit()
        con.close()
        return 0
    except:
        con.rollback()
        return -1

def get_task_progress():
    pass


'''
add worker information in MySQL
'''
def db_add_worker_info(host_name):
    try:
        con = MySQLdb.connect(ip, user_name, passwd, db_name)
        cur = con.cursor()

        sql_cmd = "INSERT INTO server_info VALUES('%s', 0, 1) ON DUPLICATE KEY UPDATE \
                last_time = 0 and state = 1" % host_name
        cur.execute(sql_cmd)
        con.commit()

        con.close()
        return 0
    except Exception, e:
        con.rollback()
        print str(e)
        return -1

'''
get worker state
'''
def db_get_worker_state(host_name):
    try:
        con = MySQLdb.connect(ip, user_name, passwd, db_name)
        cur = con.cursor()

        sql_cmd = "SELECT state FROM server_info where id = '%s'" % host_name
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        ret  = rows[0][0]
        con.close()
        return ret
    except Exception, e:
        print str(e)
        return -1

'''
update the last access time for a worker
'''
def db_update_last_access(host_name):
    try:
        con = MySQLdb.connect(ip, user_name, passwd, db_name)
        cur = con.cursor()

        cur_time = time.time()
        sql_cmd  = "update server_info set last_time = %f where id = '%s'" % (cur_time, host_name)
        cur.execute(sql_cmd)
        con.commit()
        con.close()
        return 0
    except Exception, e:
        print str(e)
        return -1

