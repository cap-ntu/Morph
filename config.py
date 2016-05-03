'''
The configuration file for system settings
'''

#the configuration of the master node
master_ip       = "10.0.146.127"
master_rpc_port = "8091"
master_rev_port = "9001"
master_snd_port = "9011"
master_path = "/root/master/"

#the configuration of the worker node
worker_path = "/root/worker/"

#the configuration of Mysql
mysql_ip        = "10.0.146.127"
mysql_user_name = "root"
mysql_password  = ""
mysql_db_name   = "morph"

#the duration for each of the video block
equal_block_dur = 60*2

#the number of threads for task preprocessing
preproc_thread_num = 10

#algorithm for task scheduling
sch_alg = 'fifo'

#default VM number
machine_num = 15

#required library for morph
mysql_support = False
neural_net_support = False


