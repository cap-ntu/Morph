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

#the number of threads for preprocessing
preproc_thread_num = 10

blk_retry_times = 3

#select the algorithm for task scheduling
sch_alg = 'fifo'
