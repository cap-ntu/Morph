#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys


def period_revenue(start_time, end_time):
    con = None
    try:
        con = lite.connect('test.db')
        cur = con.cursor()
        sql_cmd = 'SELECT * FROM Cars WHERE Cost BETWEEN 20000 AND 55000'
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        for row in rows:
            print "%s %s %s" % (row[0], row[1], row[2])
            print row

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if con:
            con.close()

period_revenue(0,1)

