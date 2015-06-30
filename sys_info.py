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
                finish_time REAL, service_type INTEGER, trans_time INTEGER, task_finished BOOLEAN)")
        con.commit()
        con.close()
        return (con, cur)
    except lite.Error, e:
        return (-1, -1)

def db_insert_task_info(task_id, service_type):
    try:
        con = lite.connect(config.db_name)
        cur = con.cursor()
        cur_time = time.time()
        sql_cmd = "INSERT INTO task_info VALUES('%s', %f, -1, %d, -1, 0)" \
                    % (task_id, cur_time, service_type)
        cur.execute(sql_cmd)
        con.commit()
        con.close()
        return 0
    except lite.Error, e:
        print e
        return -1

def get_task_progress():
    pass


