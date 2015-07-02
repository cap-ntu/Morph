#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import config
import sqlite3 as lite

def period_revenue(start_time, end_time):
    con = None
    try:
        con = lite.connect(config.db_name)
        cur = con.cursor()
        sql_cmd = 'SELECT * FROM task_info WHERE finish_time BETWEEN %f AND %f' % \
                (start_time, end_time)
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        for row in rows:
            print "%s %s %s" % (row[0], row[1], row[2])

    except lite.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()

period_revenue(1435731814.49739, 1435732481.50626)

