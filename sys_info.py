#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import config
import sqlite3 as lite

def init_db():
    try:
        con = lite.connect(config.db_name)
        cur = con.cursor()
        cur.execute("create table if not exists task_info(id TEXT, submit_time REAL, \
                finish_time REAL, service_type INTEGER, trans_time REAL, task_ongoing INTEGER)")
        con.commit()
        con.close()

        con = lite.connect(':memory:')
        cur = con.cursor()
        cur.execute("create table if not exists server_info(server_num INTEGER, server_list TEXT)")
        con.commit()
        con.close()
        return 0
    except lite.Error, e:
        return -1

def db_insert_task_info(task_id, service_type):
    try:
        con = lite.connect(config.db_name)
        cur = con.cursor()
        cur_time = time.time()
        sql_cmd = "INSERT INTO task_info VALUES('%s', %f, -1, %d, -1, 1)" \
                    % (task_id, cur_time, service_type)
        cur.execute(sql_cmd)
        con.commit()
        con.close()
        return 0
    except lite.Error, e:
        print e
        return -1

def db_update_finish_time(task_id, result):
    try:
        con = lite.connect(config.db_name)
        cur = con.cursor()
        cur_time = time.time()
        sql_cmd = "UPDATE task_info SET finish_time = %f, task_ongoing = %d WHERE id = '%s'" \
                    % (cur_time, result, task_id)
        print sql_cmd
        cur.execute(sql_cmd)
        con.commit()
        con.close()
        return 0
    except lite.Error, e:
        print e
        return -1

def get_task_progress():
    pass


