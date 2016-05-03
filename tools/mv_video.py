import os
import shutil

base_path = '/data/video_dataset/'
dest_path = '/data/video_dataset_v2/'

f = open('video.list', 'r')
lines = f.readlines()
f.close()

items = []
for line in lines:
    line = line.strip('\n')
    items.append(line)

for item in items:
    src_path = base_path + item
    dst_path = dest_path + item

    try:
        shutil.move(src_path, dst_path)
    except:
        print 'error'

    '''
    if os.path.isfile(dst_path):
        print 'yes'
    '''

