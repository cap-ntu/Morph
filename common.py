import struct

class task:
    def __init__(self):
        self.task_id    = ""
        self.file_path  = ""
        self.bitrate    = ""
        self.width      = ""
        self.height     = ""
        self.num        = 0

# task status: 0, 1, 2
class task_status:
    def __init__(self):
        self.block      = {}    #the status of each block
        self.fin_num    = 0     #the finished number of transcoding tasks
        self.progress   = 0     #the current progress of the transcoding task
        self.start_time = 0     #the time of adding the transcoding task
        self.block_num  = -1    #the total number of video blocks

block_format  = "8si200sii4s4s4si32si"

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

def pack_block_info(block):
    pack    = struct.pack(block_format, block.task_id, \
                    block.path_len,
                    block.file_path,
                    block.block_no,
                    block.total_no,
                    block.bitrate,
                    block.width,
                    block.height,
                    block.size,
                    block.md5_val,
                    block.status)
    return pack


