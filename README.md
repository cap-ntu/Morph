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

<img src="https://github.com/cap-ntu/Morph/blob/master/DOC/system.png" width="60%" height="60%">

* Interface Layer

It interacts with the users for processing the transcoding requests and preprocessing the video contents. The system provides 3 types of service interfaces, namely, command line interface (CLI), remote procedure call (RPC), and RESTful API. The users can submit the transcoding tasks and query the transcoding progress via the service interfaces. For each of the user submitted transcoding tasks, it will estimate the required computing time for the task and segment the video files into video blocks for transcoding in parallel on the workers.

* Scheduling Layer

It manages a queue of the pending tasks, and determines the execution sequence of the tasks. When there is idle computing resource in the computing cluster, the task scheduler will pick the head-of-queue task to execute. It first partitions the video file into segments, and then distributes the video segments to many workers for transcoding. After transcoding the video segments into the target resolution or bitrate, the transcoding workers will send back the transcoded video segments to the task scheduler. Finally, the task scheduler will concentrate the transcoded video segments into one video file. 

* Provisioning Layer

It manages many virtual machines, on each of which runs a transcoding worker. Since the transcoding request rate is changing over time, the resource manager layer is responsible for dynamically adjusting the number of running VMs to minimize the operational cost, according to the current workload.

![GitHub](https://github.com/cap-ntu/Morph/blob/master/DOC/workflow.png "workflow")

## Workflow

The task scheduler, after receiving the transcoding request, will first insert the incoming task into the task queue, and then determines the execution sequence of the pending task. When there is idle transcoding workers in the VM cluster, the task scheduler will select the head-of-queue task to execute. On performing a new task, the task scheduler first splits the video file into several segments, and then distributes the video segments to many transcoding workers. After a segment has been transcoded into the target resolution by the transcoding worker, it will be sent back to the task scheduler. The task scheduler continuously checks whether all of the segments of a video file have been finished. If so, it will merge the transcoded video segments into on entire video file.


The execution time for a transcoding task maybe very long if the video file is very large. To address this problem, we provide three alternative modes to perform a transcoding task. First, the system can define video segment duration in the configuration file and each of the video file would be split into video blocks according to the configuration. Each of the video blocks will be transcoded in parallel on multiple VM instances. With this method, all of the video blocks in the system have the same duration. Second, the duration of the video blocks can be determined by the task scheduling algorithms. For instance, the task scheduling algorithm can determine the duration of the video block according to the video deadline and the video size. Third, the system can perform the video transcoding without video segmentation. In this case, the entire video file will be sent to a transcoding worker directly and the transcoding task would be performed on that server. The system can select one model from the three alternatives.



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




