'''
Author: Guanyu Gao
Email:  guanyugao@gmail.com
Description: the interface for accessing the Mysql database.
'''

# !/usr/bin/python
# -*- coding: utf-8 -*-

import time
import config
import MySQLdb

ip = config.mysql_ip
passwd = config.mysql_password
user_name = config.mysql_user_name
db_name = config.mysql_db_name


class DB:
    conn = None
    cursor = None

    def __init__(self):
        self.connect()

    def connect(self):
        self.conn = MySQLdb.connect(ip, user_name, passwd, db_name)
        self.cursor = self.conn.cursor()
        self.conn.autocommit(True)

    def query(self, sql):
        try:
            self.cursor.execute(sql)

        except (AttributeError, MySQLdb.OperationalError):
            # Exception raised for errors that are related to the database's
            # like an unexpected disconnect occurs
            self.connect()
            self.cursor.execute(sql)

        except MySQLdb.Error as e:
            print ("Error %d: %s" % (e.args[0], e.args[1]))
            return False

        return self.cursor

    def is_open(self):
        """Check if the connection is open"""
        return self.conn.open

    def end(self):
        """The MySQL server will time out old connections after five minute of inactivity"""
        # Kill the connection
        if self.conn:
            self.cursor.close()
            self.conn.close()

    def lastId(self):
        """Get the last insert id"""
        return self.cursor.lastrowid

    def count_rows(self):
        return self.cursor.rowcount

    def lastQuery(self):
        """Get the last executed query"""
        try:
            return self.cursor.statement
        except AttributeError:
            return self.cursor._last_executed

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.end()


db = DB()


def init_db():
    db.query("CREATE TABLE IF NOT EXISTS task_info(id VARCHAR(100), submit_time REAL, start_time REAL, \
                        download_time REAL, finish_time REAL, service_type INTEGER, trans_time REAL, task_ongoing INTEGER)")

    db.query("CREATE TABLE IF NOT EXISTS server_info(id VARCHAR(100) NOT NULL PRIMARY KEY, \
                        last_time REAL, state INTEGER)")


def db_insert_task_info(task_id, service_type):
    cur_time = time.time()
    return db.query('INSERT INTO task_info VALUES("{task_id}", {cur_time}, -1, -1, -1, {service_type}, -1, 1)'.format(
            task_id=task_id, cur_time=cur_time, service_type=service_type))


def db_update_finish_time(task_id, result):
    cur_time = time.time()
    return db.query("UPDATE task_info SET finish_time = %f, task_ongoing = %d WHERE id = '%s'" \
                    % (cur_time, result, task_id))


def db_update_start_time(task_id):
    cur_time = time.time()
    return db.query("UPDATE task_info SET start_time = %f WHERE id = '%s'" \
                    % (cur_time, task_id))


def db_update_trans_time(task_id, trans_time):
    return db.query("UPDATE task_info SET trans_time = %f WHERE id = '%s'" \
                    % (trans_time, task_id))


def get_task_progress():
    pass


'''
add worker information in MySQL
'''


def db_add_worker_info(host_name):
    return db.query("INSERT INTO server_info VALUES('%s', 0, 1) ON DUPLICATE KEY UPDATE \
                last_time = 0 and state = 1" % host_name)


'''
get worker state
'''


def db_get_worker_state(host_name):
    cur = db.query("SELECT state FROM server_info where id = '%s' and state = 1" % host_name)
    if cur:
        return db.count_rows()

    return False


'''
update the last access time for a worker
'''


def db_update_last_access(host_name):
    cur_time = time.time()
    return db.query("update server_info set last_time = %f where id = '%s'" % (cur_time, host_name))


'''
update download time
'''


def db_update_download_time(task_id, download_time):
    return db.query("UPDATE task_info SET download_time = %f WHERE id = '%s'" \
                    % (download_time, task_id))
