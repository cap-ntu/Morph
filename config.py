#the configuration of the master node
master_ip       = "10.0.143.229"
master_rpc_port = "8091"
master_rev_port = "9001"
master_snd_port = "9011"
master_path = "/data/master/"

#the configuration of the worker node
worker_path = "/data/worker/"

#other configuration
min_seg_dur = 60*3
max_seg_dur = 60*100
equal_trans_dur = 60*3

#the number of threads for preprocessing
preproc_thread_num = 10

blk_retry_times = 3

#select the algorithm for task scheduling
sch_alg = 'fifo'

#database name
db_name = 'system_info.db'

#price decaying factor
price_decaying = 0.999

#service types
service_type = [1, 2, 3]

#pricing for different service types
#-> 1280x720, 854x480, 640x360, 426x240
#-> price per unite video duration
price_per_type = {}
s_1 = 0.08
s_2 = 0.05
s_3 = 0.02
price_per_type[1] = [s_1, s_1*0.66, s_1*0.33]
price_per_type[2] = [s_2, s_2*0.66, s_2*0.33]
price_per_type[3] = [s_3, s_3*0.66, s_3*0.33]

#amazon ec2 instance
vm_cost_per_hour = 0.252


