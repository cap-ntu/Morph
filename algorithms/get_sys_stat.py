import sys
sys.path.append("../.")
import config
import sqlite3 as lite


def get_vm_info():
    try:
        path = '../' + config.db_name
        con = lite.connect(path)
        cur = con.cursor()
        sql_cmd = "SELECT * FROM server_info WHERE id = 'current'"
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        row = rows[0]
        serv_num = row[0]
        ip_list = row[1]
        return (serv_num, ip_list)

    except lite.Error, e:
        print "Error %s:" % e.args[0]

    finally:
        con.close()

def get_pending_task():
    try:
        path = '../' + config.db_name
        con = lite.connect(path)
        cur = con.cursor()
        sql_cmd = 'SELECT * FROM task_info WHERE finish_time BETWEEN %f AND %f' % \
                (start_time, end_time)
        cur.execute(sql_cmd)
        rows = cur.fetchall()
        row = rows[0]
        serv_num = row[0]
        ip_list = row[1]
        return (serv_num, ip_list)

    except lite.Error, e:
        print "Error %s:" % e.args[0]

    finally:
        con.close()



'''
(serv_num, ip_list) = get_vm_info()
print serv_num
print ip_list
'''
