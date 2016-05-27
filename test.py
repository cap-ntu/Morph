'''
Author: Guanyu Gao
Email:  guanyugao@gmail.com
Description:
Resource management for controlling the transcoding workers
'''

import sys
import time
import config
import MySQLdb

ip        = config.mysql_ip
passwd    = config.mysql_password
user_name = config.mysql_user_name
db_name   = config.mysql_db_name

'''
get the current number of pending transcoding tasks
'''
def get_pending_task():
    try:
        con = MySQLdb.connect(ip, user_name, passwd, db_name)
        cur = con.cursor()
        sql_cmd = 'SELECT * FROM task_info WHERE task_ongoing = 1'
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        print len(rows)
        con.close()
        return 0
    except Exception, e:
        print str(e)
        return -1


if __name__ == '__main__':
    get_pending_task()



