#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import config
import sqlite3 as lite
from math import pow

decay_factor   = config.price_decaying
price_per_type = config.price_per_type
factor = 0.1 * 1.5
vm_cost = config.vm_cost_per_hour

db_name = sys.argv[1]
rate_set = [4, 2, 4, 2, 1, 2, 3, 5, 3, 4, 2, 5, 6, 5, 3, 1, 5, 3, 7, 6, 2, 6, 2, 3]

def period_revenue(start_time, end_time):
    con = None
    cost = 0
    revenue  = 0
    task_num = 0

    try:
        con = lite.connect(db_name)
        cur = con.cursor()

        sql_cmd = 'select min(submit_time) from task_info'
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        start_time = rows[0][0]

        for k in range(0, 24):
            cost = 15 * (k+1) * vm_cost / 2.0
            revenue = 0
            epch_start = start_time
            epch_end   = start_time + (k + 1) * 1800
            sql_cmd = 'SELECT *  FROM task_info WHERE finish_time BETWEEN %f AND %f' % \
                (epch_start, epch_end)
            cur.execute(sql_cmd)
            rows = cur.fetchall()

            '''
            0: id TEXT, 1: submit_time REAL, 2: start_time, 3: finish_time REAL, 4: service_type INTEGER,\
                5: trans_time REAL, 6: task_ongoing INTEGER
            '''
            for row in rows:
                if row[6] == 0 or row[6] == -3:
                    #print "%s %s %s" % (row[0], row[1], row[2])
                    task_revenue = factor * pow(decay_factor, row[3] - row[1]) * (row[5] / 60.0) * price_per_type[row[4]]
                    revenue += task_revenue
                    task_num += 1
                    #print row[4]
            print (revenue - cost)





        return (revenue, task_num)

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



