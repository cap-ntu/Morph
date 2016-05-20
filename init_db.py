'''
Author: Guanyu Gao
Email:  guanyugao@gmail.com
Description: This program is used to initialize the Mysql database.
'''

#!/usr/bin/python

import config
import MySQLdb

ip        = config.mysql_ip
passwd    = config.mysql_password
user_name = config.mysql_user_name
db_name   = config.mysql_db_name

print 'Mysql server information'
print 'host ip:'   + ip
print 'user name:' + user_name
print 'password:'  + passwd
print 'database name:' + db_name


if __name__ == '__main__':

    db = MySQLdb.connect(ip, user_name, passwd)
    with db:

        cursor = db.cursor()

        print 'create the database in Mysql:' + db_name
        sql = 'create database if not exists ' + db_name
        cursor.execute(sql)

        print 'use the database:' + db_name
        sql = 'use ' + db_name
        cursor.execute(sql)

        print 'create table:' + 'task_info'
        sql = "create table if not exists task_info(id VARCHAR(100), submit_time REAL, start_time REAL, \
                finish_time REAL, service_type INTEGER, trans_time REAL, task_ongoing INTEGER)"
        cursor.execute(sql)

        sql = "create table if not exists server_info(id VARCHAR(100) NOT NULL PRIMARY KEY, last_time REAL, state INTEGER)"
        cursor.execute(sql)




