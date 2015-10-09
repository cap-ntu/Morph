'''
The configuration file for system settings
'''

#the configuration of the master node
master_ip       = "10.0.143.229"
master_rpc_port = "8091"
master_rev_port = "9001"
master_snd_port = "9011"
master_path = "/data/master/"

#the configuration of the worker node
worker_path = "/data/worker/"

#the duration for each of the video block
min_seg_dur = 60*2
max_seg_dur = 60*100
equal_trans_dur = 60*2

#the number of threads for task preprocessing
preproc_thread_num = 10

#not in use
blk_retry_times = 3

#algorithm for task scheduling
sch_alg = 'vbs'

#database for system information
db_name = 'system_info_vbs.db'

#price decaying factor
price_decaying = 0.999

#service types
service_type = [1, 2, 3]

#pricing for different service types
#-> 1280x720, 854x480, 640x360, 426x240
#-> price per unite video duration
price_per_type = {}

#price for transcoding service
#price_per_type[1] = 0.08
#price_per_type[2] = 0.05
#price_per_type[3] = 0.02

price_per_type[1] = 0.018
price_per_type[2] = 0.012
price_per_type[3] = 0.006


#cost for renting vm instances
vm_cost_per_hour = 0.252

#default VM number
machine_num = 15

video_split = False
