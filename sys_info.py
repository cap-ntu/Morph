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
        cur.execute("create table if not exists task_info(id TEXT, submit_time REAL, start_time REAL, \
                finish_time REAL, service_type INTEGER, trans_time REAL, task_ongoing INTEGER)")
        con.commit()

        cur.execute("create table if not exists server_info(server_num INTEGER, server_list TEXT, id TEXT)")
        con.commit()
        sql_cmd = "DELETE FROM server_info WHERE id = 'current'"
        cur.execute(sql_cmd)
        con.commit()
        sql_cmd = "INSERT INTO server_info VALUES(-1, '', 'current')"
        cur.execute(sql_cmd)
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
        sql_cmd = "INSERT INTO task_info VALUES('%s', %f, -1, -1, %d, -1, 1)" \
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

def db_update_start_time(task_id):
    try:
        con = lite.connect(config.db_name)
        cur = con.cursor()
        cur_time = time.time()
        sql_cmd = "UPDATE task_info SET start_time = %f WHERE id = '%s'" \
                    % (cur_time, task_id)
        print sql_cmd
        cur.execute(sql_cmd)
        con.commit()
        con.close()
        return 0
    except lite.Error, e:
        print e
        return -1


def db_update_trans_time(task_id, trans_time):
    try:
        con = lite.connect(config.db_name)
        cur = con.cursor()
        sql_cmd = "UPDATE task_info SET trans_time = %f WHERE id = '%s'" \
                    % (trans_time, task_id)
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

def set_server_num(num, serv_list):
    try:
        con = lite.connect(config.db_name)
        cur = con.cursor()
        sql_cmd = "UPDATE server_info SET server_num = %d, server_list = '%s' WHERE id = 'current'" \
                    % (num, serv_list)
        cur.execute(sql_cmd)
        con.commit()
        con.close()
        return 0
    except lite.Error, e:
        print e
        return -1















