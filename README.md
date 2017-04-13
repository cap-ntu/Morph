## Morph: A Fast and Scalable Cloud Transcoding System

## Contents 
-------------------
* [Overview](#overview)
* [Workflow](#workflow)
* [Installation](#installation)
* [Programming Interface](#programming-interface)
* [Basic Usage](#basic-usage)
* [Advanced Usage](#advanced-usage)
* [Performance](#performance)
* [License](#license)
* [Contact](#contact)

## Overview
Morph is an open source cloud transcoding system. It can leverage the scalability of the cloud infrastructure to encode and transcode the video files in fast speed, and dynamically provision the computing resource to accommodate the time-varying workload. Morph is implemented in Python. It can be accessed via RESTful API, command line interface (CLI), and RPC. 

The system architecture is shown in the following figure. The system is composed of the following layers:

<img src="https://raw.githubusercontent.com/cap-ntu/Morph/master/DOC/system.png" width="40%" height="40%">

* Interface Layer

It interacts with the users for processing the transcoding requests and preprocessing the video contents. The system provides 3 types of service interfaces, namely, command line interface (CLI), remote procedure call (RPC), and RESTful API. The users can submit the transcoding tasks and query the transcoding progress via the service interfaces. For each of the user submitted transcoding tasks, it will estimate the required computing time for the task and segment the video files into video blocks for transcoding in parallel on the workers.

* Scheduling Layer

The user submitted transcoding tasks will be put into the scheduling queue. The task scheduler sequences the pending tasks in the queue according to the scheduling policy and the QoS profiles of the tasks. Whenever the master node receives a transcoding request from the worker, the task scheduler will select a video block from the pending tasks for dispatching by applying the scheduling policy. The transcoded video blocks on the worker will be sent back to the master for concentration.

* Provisioning Layer

It manages the transcoding workers for dynamic resource provisioning. Our system can adopt the virtual machines (e.g., KVM ) or containers (e.g., Docker) for resource virtualization. Each VM instance or container runs a worker. The worker will request a video block from the master node whenever it it idle. The worker will transcode the video block into the target representations, which will be sent back to the master node.

## Workflow

<img src="https://raw.githubusercontent.com/cap-ntu/Morph/master/DOC/workflow.png" width="80%" height="80%">

The user submit a transcoding task by uploading a video file and specifying the transcoding parameters. The video content will be segmented into independent video blocks according to the group of pictures (GOP) structure. The video block information of the task will be then put into the scheduling queue. 

When an idle worker requests a video block from the master node, the scheduler determines which video block in the scheduling queue will be selected for dispatching by applying the scheduling policy. The worker will transcode the video block into the target representation, and then send back the target representation to the master node. The video blocks in the scheduling queue can be requested and transcoded by the workers in parallel. 

The master node continuously checks the transcoding status of the video blocks of each task. If all the video blocks of a task have been finished successfully, the master node will concentrate the video blocks into one video file. Then, the transcoding task is finished and the target representations of the video content are ready to be downloaded by the users.


## Installation

System Requirement

* [ubuntu 14.04](http://releases.ubuntu.com/14.04/)
* [Python 2.7.6](https://www.python.org/download/releases/2.7.6/)
* [ffmpeg](https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu)
* [Mysql](https://help.ubuntu.com/12.04/serverguide/mysql.html)

Please click the above links for the installation of the dependent software.

It may require to install some lacked libraries, e.g., pycurl, mysqldb.
```bash
sudo apt-get update    
sudo apt-get install python-pycurl
sudo apt-get install python-mysqldb
sudo apt-get install python-numpy
```

Step 1: Clone the code from Github

```bash
git clone https://github.com/cap-ntu/Morph.git
```

Step 2: Revise the configuration file **config.py**

All executable programs read the configuration information from config.py.
Make sure each item is set with appropriate value according to your system configuration.

```bash

#the IP address of the master node
master_ip       = "127.0.0.1"

#Remain unchanged
master_rpc_port = "8091" 
master_rev_port = "9001"
master_snd_port = "9011"

#The working path of the master node, keep unchanged
master_path = "./master/"

#The working path of the worker node, keep unchanged
worker_path = "./worker/"

#the configuration of Mysql
mysql_ip        = "127.0.0.1"
mysql_user_name = "root"
mysql_password  = ""

#Remain unchanged 
mysql_db_name   = "morph"

#the duration for each of the video block
equal_block_dur = 60*2

#the number of threads for task preprocessing
preproc_thread_num = 10

#algorithm for task scheduling
sch_alg = 'fifo'

```

Step 3: Initialize the database and tables in Mysql   
```bash
python init_db.py
```

Step 4: Change to the directory 'Morph', and start up the Master node by executing the following command.
```bash
nohup python master.py > master_error_msg &
```

Step 5: Change to the directory 'Morph', start up the Worker node. This needs to be executed on each of the worker node. 
```bash
nohup python worker.py > worker_error_msg &
```

Step 6: Check the log and the error message of the master node.
```bash
tail master_error_msg
tail master.*.log
```

Check the log and the error message of the worker nodes.
```bash
tail worker_error_msg
tail worker.*.log
```

## Programming Interface
-------------------

The system provides three kinds of interface for accessing the service, including Restful API, Command Line Interface, and RPC. The users can use these interfaces to submit new transcoding tasks and to query the transcoding progress of a task.

### Restful API

The parameters of HTTP POST method for submitting a new task. The video location is specified with URL. 

<html>

     'url': 'http://155.69.52.158/test.mp4',
     'target_resolution': '100x100 200x200',
     'priority': 5
     
</html>

The parameters of HTTP POST method for submitting a new task. The video location is specified with a local path. The video file will be uploaded to the server for video transcoding. 

<html>

     'video_file': open('/home/Public/test.mp4','rb'),
     'target_resolution': '100x100 200x200',
     'priority': 5
 
</html>

The parameter of HTTP Post method for querying the task status. 

<html>

     url = 'http://155.69.52.158/transcoder/get_progress'
     key = {'key' : 'G8QKmGXX'}
     
</html>

### Command Line

Parameters for the command line:
<html>

     -l: local video file
     -u: url of the video file
     -p: priority (optional)
     -s: target resolutions
     
</html>

Submit a new transcoding task by CLI
```bash
python cli_submit.py -l /home/Videos/test.mp4 -s 640x360 426x240
```

Query task status

```bash
python cli_query.py –k taskid
```

### RPC

We adopt [SimpleXMLRPCServer](https://docs.python.org/2/library/simplexmlrpcserver.html) for implementing RPC, the APIs for submitting transcoding task and querying task status are as follows:

Submit a new transcoding task (URI can be a URL or local file path)
```bash
put_trans_task(URI, bitrate, width, height, priority, task_id = None)
```

Query the task status
```bash
get_progress(task_id)
```


## Basic Usage

The easiest way to use this software is via command line. With this method, you do not need to configure the webserver or write the code for calling RPC. There are two programs serving as the command line, **cli_query.py** and **cli_submit.py**. Note that the **config.py** should be kept a copy with these two programs, since they need to the configuration information from it. 

* Submit a transcoding task by the command line  

```bash
python cli_submit.py -l /home/Videos/test.mp4 -s 640x360 426x240
Return: Task ID
```
In the above command, the file path of the original video file is '/home/Videos/test.mp4', specified by '-l'. This needs to be a valid local video file in the master node. The taget resolutions are 640x360, 426x240, specified by '-s'.

```bash
python cli_submit.py -u http://aidynamic.com/video/bunny.mp4 -s 640x360 426x240
Return: Task ID
```
The user can also specify the URL of the original video file by '-u' to submit a task. In the above command, the URL of the original video file is 'http://aidynamic.com/video/bunny.mp4', specified by '-u'. The master node will first download the video file and then perform the transcoding operations. 

* Query the transcoding progress of a task with the task ID
```bash
python cli_query.py –k ddsdd123
Return: 
1. Progress of the task.
2. The file path of the target video file if it has been finished. 
```
In the above command, the task ID is 'ddsdd123', specified by '-k'. 

## Advanced Usage
We can start the controller to dynamically control the transcoding workers. To do this, we first need to add the information of the available VM instances or containers to the file **vm.list**. In this file, each line corresponds to the host name of an instance or a container. We can execute the command **hostname** to obtain the name of an instance or a container, and then, file the host name into the file **vm.list**. After that, we can start the controller.
```bash
python controller.py
```
We can observe the state of each worker in the MySQL database.
```bash
use morph
select * from server_info;
```
The worker node will read the value of the field **state** from the database to control itself. 

## Performance
The duration of the test video file is 138 minutes. The resolution is 1920x1080, and the bitrate is 2399 kb/s. The video data is encoded in H.264, and the audio data is encoded in AAC. The CPU frequency of the servers is 2.10GHz. The master node is allocated with 8 CPU cores, and the memory size is 8GB. The worker node is allocated with 4 CPU cores, and the memory size is 2GB. We use the Docker for the resource allocation. 

We first measure the video segmentation time for splitting the video file into equal-duration video blocks. The duration of each video block is 2 minutes. The FFmpeg command for the video segmentation is show as follow:

```bash
ffmpeg –i PV4h.mp4 -f segment -segment_time 120 -c copy -map 0 -segment_list PV4h.list PV4h_%03d_.mp4
```

The video segmentation time for the video file is 46 seconds.

We then measure the transcoding time for the test video file with different number of transcoding workers. The target resolution is 480x360. We illustrate the transcoding time in the following table:

| Worker Number  | FFmpeg | 1 | 5     | 10    | 15    | 20    | 25    | 30    |
|------------------   |------  |------ |------   |------   |------   |------   |------   |------   |
| Transcoding Time (s)  | 1775 | 1843 | 605   | 369   | 271   | 213   | 194   | 181   |
| Speed-up Ratio    | 1x  | 0.96x | 2.9x  | 4.8x  | 6.5x  | 8.3x  | 9.1x  | 9.8x  |

The transcoding time for using a standalone FFmpeg on a single server is 1775 seconds. If the system has only one active worker, the transcoding time is 1843 seconds, which is larger than the standalone ffmpeg. The overhead comes from the video segmentation, transmission, and concentration for transcoding the video file in a distributed manner. With more active workers to transcode the video blocks in parallel, the overall transcoding time decreases, achieving larger speed-up ratio. 

The FFmpeg command for video block concentration is as follow
```bash
ffmpeg -f concat –i PV4h_480x360.list -c copy PV4h_480x360.mp4
```
The video block concentration time is 13 seconds. 



## License
THIS SOFTWARE IS RELEASED UNDER THE MIT LICENSE (MIT)
Copyright (c), 2015, NTU CAP

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Contact
If you find any problem with this software, please feel free to contact us, your feedback is appreciated. 

Email: guanyugao@gmail.com; ggao001@e.ntu.edu.sg






