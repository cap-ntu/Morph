#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import config
import sqlite3 as lite
from math import pow

decay_factor = config.price_decaying

def period_revenue(start_time, end_time):
    con = None
    revenue = 0
    try:
        con = lite.connect(config.db_name)
        cur = con.cursor()
        sql_cmd = 'SELECT * FROM task_info WHERE finish_time BETWEEN %f AND %f' % \
                (start_time, end_time)
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        '''
        id TEXT, submit_time REAL, finish_time REAL, service_type INTEGER,\
                trans_time REAL, task_ongoing INTEGER
        '''
        for row in rows:
            if row[5] == 0:
                #print "%s %s %s" % (row[0], row[1], row[2])
                task_revenue = pow(decay_factor, row[2] - row[1]) * row[3] * row[4]
                revenue += task_revenue
        return revenue

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        return None

    finally:
        if con:
            con.close()

r = period_revenue(1435938011.92517, 1436076176.82975)
print r
