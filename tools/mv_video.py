import shutil

base_path = '/data/video_dataset/'
dest_path = '/data/new_video_dataset/'

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
    shutil.move(src_path, dst_path)
