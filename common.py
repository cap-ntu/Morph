import sys
import json
import struct
import logging
from random import Random

# This function is used to generate a random string as the key of the task
def gen_key(randomlength = 8):
    str     = ''
    chars   = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length  = len(chars) - 1
    random  = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

class task:
    def __init__(self):
        self.task_id    = ""    #the id of the task
        self.file_path  = ""    #the file path or the URL of the submitted video
        self.bitrate    = ""    #target bitrate
        self.width      = ""    #target resolution
        self.height     = ""    #target resolution
        self.priority   = 0     #task priority
        self.block      = {}    #the status of each block
        self.fin_num    = 0     #the finished number of transcoded blocks
        self.progress   = 0.0   #the current progress of the transcoding task
        self.start_time = 0     #the time of adding the transcoding task
        self.block_num  = -1    #the total number of video blocks
        self.end_time   = 0     #the finish time of the task
        self.est_time   = 0     #estimated transcoding time for this task
        self.deadline   = 0     #the deadline for this task
        self.value      = 0     #the estimated value for scheduling

block_format  = "50si200sii4s30s30si32siii"

class block:
    def __init__(self):
        self.task_id    = ""
        self.path_len   = 0
        self.file_path  = ""
        self.block_no   = 0
        self.total_no   = 0
        self.bitrate    = ""
        self.width      = ""
        self.height     = ""
        self.size       = 0
        self.md5_val    = ""
        self.status     = 0
        self.st_time    = 0
        self.retry      = 0

def pack_block_info(block):
    block.task_id = block.task_id.ljust(50)
    pack = struct.pack(block_format, block.task_id, \
                    block.path_len,
                    block.file_path,
                    block.block_no,
                    block.total_no,
                    block.bitrate,
                    block.width,
                    block.height,
                    block.size,
                    block.md5_val,
                    block.status,
                    block.st_time,
                    block.retry)
    return pack

def unpack_block_info(block, data):
    (block.task_id,   \
     block.path_len,  \
     block.file_path, \
     block.block_no,  \
     block.total_no,  \
     block.bitrate,   \
     block.width,     \
     block.height,    \
     block.size,      \
     block.md5_val,   \
     block.status,    \
     block.st_time,   \
     block.retry)     = struct.unpack(block_format, \
                        data[0: struct.calcsize(block_format)])
    block.task_id = block.task_id.strip()


format_length = "iqqqqqq"

def init_log_module(logger_name, ip, level):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    fh = logging.FileHandler(logger_name + '.' + ip + '.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

class dump_msg(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        return '%s' % json.dumps(self.kwargs)


