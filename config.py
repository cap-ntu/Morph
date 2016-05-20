'''
The configuration file for system settings
'''
import os

#the configuration of the master node
master_ip       = "127.0.0.1"
master_rpc_port = "8091"
master_rev_port = "9001"
master_snd_port = "9011"
master_path = "./master_data/"

#the configuration of the worker node
worker_path = "./worker_data/"

#the configuration of Mysql
mysql_ip        = "127.0.0.1"
mysql_user_name = "root"
mysql_password  = "123"
mysql_db_name   = "morph"

#the duration for each of the video block
equal_block_dur = 60*2

#the number of threads for task preprocessing
preproc_thread_num = 10

#algorithm for task scheduling
sch_alg = 'fifo'


master_path = os.path.abspath(master_path)
worker_path = os.path.abspath(worker_path)

if not os.path.exists(master_path):
    os.makedirs(master_path)

if not os.path.exists(worker_path):
    os.makedirs(worker_path)


