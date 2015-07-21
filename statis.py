#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import config
import sqlite3 as lite
from math import pow

decay_factor   = config.price_decaying
price_per_type = config.price_per_type

db_name = sys.argv[1]
rate_set = [4, 2, 4, 2, 1, 2, 3, 5, 3, 4, 2, 5, 6, 5, 3, 1, 5, 3, 7, 6, 2, 6, 2, 3]

def period_revenue(start_time, end_time):
    con = None
    revenue  = 0
    task_num = 0
    latency  = {}
    latency[1] = 0
    latency[2] = 0
    latency[3] = 0

    task_type = {}
    task_type[1] = 0
    task_type[2] = 0
    task_type[3] = 0

    try:
        con = lite.connect(db_name)
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
            if row[6] == 0 or row[6] == -3:
                #print "%s %s %s" % (row[0], row[1], row[2])
                task_revenue = pow(decay_factor, row[3] - row[1]) * (row[5] / 60.0) * price_per_type[row[4]]
                revenue += task_revenue
                task_num += 1
                #print row[4]
                latency[row[4]] += (row[2] - row[1])
                task_type[row[4]] += 1

        '''
        print 'task num:', task_num
        print 'type 1 latency:', latency[1] / task_type[1]
        print 'type 2 latency:', latency[2] / task_type[2]
        print 'type 3 latency:', latency[3] / task_type[3]

        print 'type 1 num:', task_type[1]
        print 'type 2 num:', task_type[2]
        print 'type 3 num:', task_type[3]
        '''

        sql_cmd = 'select min(submit_time) from task_info'
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        start_time = rows[0][0]

        sql_cmd = 'select max(finish_time) from task_info'
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        fin_time = rows[0][0]

        dur = (fin_time - start_time) / 60.0

        for k in range(0, 24):
            epch_start = start_time + k * 1800
            epch_end   = start_time + (k + 1) * 1800
            sql_cmd = 'SELECT COUNT(*) FROM task_info WHERE submit_time BETWEEN %f AND %f' % \
                (epch_start, epch_end)
            cur.execute(sql_cmd)
            rows = cur.fetchall()
            num = rows[0][0]
            print num, '  ',
            print 'estimated:', rate_set[k] * 30 / 7


        return (revenue, task_num, dur)

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        return None

    finally:
        if con:
            con.close()


s = 0
t = time.time()
r = period_revenue(s, t)
print r

#print 'duration:', (t - s) /60.0



