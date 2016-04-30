##Morph: A Fast and Scalable Cloud Transcoding System

##Contents 
-------------------
* [Overview](#overview)
* [Workflow](#workflow)
* [Installation](#installation)
* [Getting Started](#getting-started)
* [Example](#example)

## Overview
Morph is an open source cloud transcoding system. It can leverage the scalability of the cloud infrastructure to encode and transcode the video files in fast speed, and dynamically provision the computing resource to accommodate the time-varying workload. Morph is implemented in Python. It can be accessed via RESTful API, command line interface (CLI), and RPC. 

The system architecture is shown in the following figure. The system is composed of the following layers:

<img src="https://github.com/cap-ntu/Morph/blob/master/DOC/system.png" width="40%" height="40%">

* Interface Layer

It interacts with the users for processing the transcoding requests and preprocessing the video contents. The system provides 3 types of service interfaces, namely, command line interface (CLI), remote procedure call (RPC), and RESTful API. The users can submit the transcoding tasks and query the transcoding progress via the service interfaces. For each of the user submitted transcoding tasks, it will estimate the required computing time for the task and segment the video files into video blocks for transcoding in parallel on the workers.

* Scheduling Layer

The user submitted transcoding tasks will be put into the scheduling queue. The task scheduler sequences the pending tasks in the queue according to the scheduling policy and the QoS profiles of the tasks. Whenever the master node receives a transcoding request from the worker, the task scheduler will select a video block from the pending tasks for dispatching by applying the scheduling policy. The transcoded video blocks on the worker will be sent back to the master for video concentration.

* Provisioning Layer

It manages the transcoding workers for dynamic resource provisioning. Our system can adopt the virtual machines (e.g., KVM ) or containers (e.g., Docker) for resource virtualization. Each VM instance or container runs a worker. The worker will request a video block from the master node whenever it it idle. The worker will transcode the video block into the target representations, which will be sent back to the master node.

## Workflow

<img src="https://github.com/cap-ntu/Morph/blob/master/DOC/workflow.png" width="80%" height="80%">

The user submit a transcoding task by uploading a video file and specifying the transcoding parameters. The video content will be segmented into independent video blocks according to the group of pictures (GOP) structure. The video block information of the task will be then put into the scheduling queue. 

When an idle worker requests a video block from the master node, the scheduler determines which video block in the scheduling queue will be selected for dispatching by applying the scheduling policy. The worker will transcode the video block into the target representation, and then send back the target representation to the master node. The video blocks in the scheduling queue can be requested and transcoded by the workers in parallel. 

The master node continuously checks the transcoding status of the video blocks of each task. If all the video blocks of a task have been finished successfully, the master node will concentrate the video blocks into one video file. Then, the transcoding task is finished and the target representations of the video content are ready to be downloaded by the users.


## Installation

System Requirement (required libraries)

* [ubuntu 14.04](http://releases.ubuntu.com/14.04/)
* [Python 2.7.6](https://www.python.org/download/releases/2.7.6/)
* [NeuroLab](https://pythonhosted.org/neurolab/)
* [Redis](http://redis.io/)
* [Video Converter](https://github.com/senko/python-video-converter)
* [ffmpeg](https://www.ffmpeg.org/)
* [SQLite](https://www.sqlite.org/)

Step 1: Clone the code from Github

`https://github.com/cap-ntu/Morph.git`

Step 2: System Configuration

`Set the values of the items in config.py according to system information and requirements.`

Step 3: Start up the Master node


`nohup python master.py &`

Step 4: Start up the Worker node

`nohup python worker.py &`

## Getting Started
-------------------

The system provides three kinds of interface for providing video transcoding service, including Restful API, Command Line Interface, and RPC. In general, the system interfaces can be divided into two categories: task submission and status query. Task submission is to submit a transcoding task to the system by specifying parameters. Status query is to query the progress of the transcoding task. The details of each kind of interfaces are given in the following sections.

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
     -t: task id (optional)
     -p: priority (optional)
     -s: resolution

</html>

Submit a new transcoding task by CLI

`python submit_task.py -l /home/Videos/test.mp4 -s 640x360 426x240`

Query task status

`python query.py –k taskid`

### RPC

We adopt the SimpleXML as the RPC library, the APIs for submitting transcoding task and querying task status are as follows:

Submit a new transcoding task (URI can be a URL or local file path)

`put_trans_task(URI, bitrate, width, height, priority, task_id = None)`

Query the task status

`get_progress(task_id)`


## Example

Submit a transcoding task by the command line interface: 

the file path of the original video file is '/home/Videos/test.mp4', specified by '-l'

The taget resolutions are 640x360, 426x240, specified by '-s'

`python submit_task.py -l /home/Videos/test.mp4 -s 640x360 426x240`

Query the progress of the task with the ID 'ddsdd123', specified by '-k'

`python query.py –k ddsdd123`

## [Wiki](https://github.com/cap-ntu/Morph/wiki)
## [Issues](https://github.com/cap-ntu/Morph/issues)




