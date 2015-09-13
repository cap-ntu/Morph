
Cloud Video Transcoding System
==============================

1. Installation
-----------

System Requirement
[NeuroLab](https://pythonhosted.org/neurolab/)


2. System Interface
-------------------

The system provides three kinds of interface for providing video transcoding service, including Restful API, Command Line Interface, and RPC. In general, the system interfaces can be divided into two categories: task submission and status query. The details of each kind of interfaces are given in the following sections.

###2.1 Restful API Interface

The parameters of HTTP POST method for submitting a new task. The video location is specified with URL. 

<html>

     'url': 'http://155.69.52.158/guanyu.mp4',
     'target_resolution': '100x100 200x200',
     'priority': 5
     
</html>

The parameters of HTTP POST method for submitting a new task. The video location is specified with a local path. The video file will be uploaded to the server for video transcoding. 

<html>

     'video_file': open('/home/guanyu/Public/guanyu.mp4','rb'),
     'target_resolution': '100x100 200x200',
     'priority': 5
 
</html>

The parameter of HTTP Post method for querying the task status. 

<html>

     url = 'http://155.69.52.158/transcoder/get_progress'
     key = {'key' : 'G8QKmGXX'}
     
</html>

###2.2 Command Line Interface

Parameters for the command line:
<html>

     -l: local video file
     -u: url of the video file
     -t: task id (optional)
     -p: priority (optional)
     -s: resolution

</html>

Submit a new transcoding task by CLI

`python submit_task.py -l /home/Videos/lvjuren/lvjuren.mp4 -s 640x360 426x240`

Query task status

`python query.py –k taskid`

###2.3 RPC Interface

We adopt the SimpleXML as the RPC library, the APIs for submitting transcoding task and querying task status are as follows:

Submit a new transcoding task (URI can be a URL or local file path)

`put_trans_task(URI, bitrate, width, height, priority, task_id = None)`

Query the task status

`get_progress(task_id)`









