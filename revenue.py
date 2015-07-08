#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import config
import sqlite3 as lite
from math import pow

decay_factor   = config.price_decaying
price_per_type = config.price_per_type

def period_revenue(start_time, end_time):
    con = None
    revenue  = 0
    task_num = 0
    latency  = 0
    try:
        con = lite.connect(config.db_name)
        cur = con.cursor()
        sql_cmd = 'SELECT * FROM task_info WHERE finish_time BETWEEN %f AND %f' % \
                (start_time, end_time)
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        '''
        0: id TEXT, 1: submit_time REAL, 2: start_time, 3: finish_time REAL, 4: service_type INTEGER,\
                5: trans_time REAL, 6: task_ongoing INTEGER
        '''
        for row in rows:
            if row[6] == 0:
                #print "%s %s %s" % (row[0], row[1], row[2])
                task_revenue = pow(decay_factor, row[3] - row[1]) * (row[5] / 60.0) * price_per_type[row[4]]
                revenue += task_revenue
                task_num += 1
                #print task_revenue
                latency += (row[2] - row[1])

        print 'task num:', task_num
        return (revenue, latency/task_num, task_num)

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        return None

    finally:
        if con:
            con.close()

r = period_revenue(1436356584.9515, 1436357729.02912)
print r
