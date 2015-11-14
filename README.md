Morph: Cloud Transcoding Management System
==============================
1. Overview
-------------------

Our system provides cost-efficient and QoS-guaranteed cloud-based video transcoding service. It consists of three layers, including the Service Interface Layer, Task Scheduling Layer, and Resource Management Layer. The functionalities of each layer are detailed as follows: 

![GitHub](https://github.com/springlake/akilos/blob/master/DOC/system.png "system")

####Service Interface Layer

It handles the user requests for submitting new transcoding tasks, querying task status and obtaining the transcoded video files. It provides two kinds of interfaces for the video transcoding service, including Restful API and Command Line Interface (CLI). With the Restful API interface, users can submit the request through HTTP POST/GET method; with CLI, users can submit the request by executing command line on the system background.

####Task Scheduling Layer

It manages a queue of the pending tasks, and determines the execution sequence of the tasks. When there is idle computing resource in the computing cluster, the task scheduler will pick the head-of-queue task to execute. It first partitions the video file into segments, and then distributes the video segments to many workers for transcoding. After transcoding the video segments into the target resolution or bitrate, the transcoding workers will send back the transcoded video segments to the task scheduler. Finally, the task scheduler will concentrate the transcoded video segments into one video file. 

####Resource Management Layer

It manages many virtual machines, on each of which runs a transcoding worker. Since the transcoding request rate is changing over time, the resource manager layer is responsible for dynamically adjusting the number of running VMs to minimize the operational cost, according to the current workload.


2. Installation
-----------

System Requirement

* [NeuroLab](https://pythonhosted.org/neurolab/)
* [Redis](http://redis.io/)
* [Video Converter](https://github.com/senko/python-video-converter)
* [ffmpeg](https://www.ffmpeg.org/)
* [SQLite](https://www.sqlite.org/)

Clone the code from Github

`https://github.com/springlake/akilos`

System Configuration

`Set the values of the items in config.py according to system information and requirements.`

Start up the Master node


`nohup python master.py &`

Start up the Worker node

`nohup python worker.py &`

3. Getting Started
-------------------

The system provides three kinds of interface for providing video transcoding service, including Restful API, Command Line Interface, and RPC. In general, the system interfaces can be divided into two categories: task submission and status query. The details of each kind of interfaces are given in the following sections.

###3.1 Restful API

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

###3.2 Command Line

Parameters for the command line:
<html>

     -l: local video file
     -u: url of the video file
     -t: task id (optional)
     -p: priority (optional)
     -s: resolution

</html>

Submit a new transcoding task by CLI

`python submit_task.py -l /home/Videos/test.mp4 -s 640x360 426x240`

Query task status

`python query.py –k taskid`

###3.3 RPC

We adopt the SimpleXML as the RPC library, the APIs for submitting transcoding task and querying task status are as follows:

Submit a new transcoding task (URI can be a URL or local file path)

`put_trans_task(URI, bitrate, width, height, priority, task_id = None)`

Query the task status

`get_progress(task_id)`


4. Example
-----------
Submit a transcoding task, the file path of the original video file is '/home/Videos/test.mp4' 

The taget resolutions are 640x360, 426x240

`python submit_task.py -l /home/Videos/test.mp4 -s 640x360 426x240`

Query the progress of the task with the ID 'ddsdd123'

`python query.py –k ddsdd123`

[5. Wiki](https://github.com/cap-ntu/Morph/wiki)
-----------
[6. Issues](https://github.com/cap-ntu/Morph/issues)
-----------




