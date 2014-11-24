import struct

class task:
    def __init__(self):
        self.task_id    = ""
        self.file_path  = ""
        self.bitrate    = 0
        self.width      = ""
        self.height     = ""
        self.num        = 0

# task status: 0, 1, 2
class task_status:
    def __init__(self):
        self.block      = None
        self.status     = 0
        self.progress   = 0

block_format  = "8si200siiiiii32si"

class block:
    def __init__(self):
        self.task_id    = ""
        self.path_len   = 0
        self.file_path  = ""
        self.block_no   = 0
        self.total_no   = 0
        self.bitrate    = 0
        self.width      = 0
        self.height     = 0
        self.size       = 0
        self.md5_val    = ''
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


