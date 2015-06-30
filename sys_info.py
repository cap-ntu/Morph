#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sqlite3 as lite

def init_db():
    try:
        con = lite.connect('system_info.db')
        cur = con.cursor()
        cur.execute("create table if not exists task_info(id TEXT, submit_time INTEGER, finish_time INTEGER, service_type INTEGER)")
        return (con, cur)
    except lite.Error, e:
        return (-1, -1)

def insert_task_info():
    pass

def get_task_progress():
    pass


