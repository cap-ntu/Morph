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
m_num = [11, 6, 13, 8, 5, 6, 10, 17, 11, 13, 8, 16, 20, 15, 13, 3, 16, 9, 20, 20, 8, 17, 8, 9];

#m_num = [11, 6, 13, 7, 5, 6, 10, 17, 13, 14, 8, 14, 21, 15, 10, 4, 14, 11, 23, 19, 8, 18, 8, 10];

#for hvs
m_num = [11, 6, 13, 7, 7, 6, 13, 17, 11, 14, 8, 16, 20, 14, 10, 3, 16, 9, 21, 21, 8, 18, 8, 11];

#rate_set = [4, 2, 4, 2, 1, 2, 3, 5, 3, 4, 2, 5, 6, 5, 3, 1, 5, 3, 7, 6, 2, 6, 2, 3]
#m_num = [x*3 for x in rate_set]

#for vbs_new_policy
#m_num = [10, 5, 12, 6, 5, 5, 11, 15, 9, 14, 7, 14, 19, 14, 10, 4, 14, 9, 19, 19, 8, 17, 9,8];


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
            #cost = 15 * (k+1) * vm_cost / 2.0
            #cost = 10 * (k+1) * vm_cost / 2.0
            #cost = 5 * (k+1) * vm_cost / 2.0
            cost = sum(m_num[0:k+1]) * vm_cost / 2.0

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
            print (revenue - cost) * 0.95





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



