import struct

block_format  = "8si200siiiiii32s"
class block:
    def __init__(self):
        self.task_id    = ""
        self.path_len   = -1
        self.file_path  = ""
        self.block_no   = -1
        self.total_no   = -1
        self.bitrate    = -1
        self.width      = -1
        self.height     = -1
        self.size       = -1
        self.md5_val    = ''

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
                    block.md5_val)
    return pack
