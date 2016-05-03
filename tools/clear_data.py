import os

file_name = 'task_key.1'
file_path = '/data/master/'

f = open(file_name)
lines = f.readlines()

for key in lines:
    key = key.replace('\n', '')
    cmd = 'rm -f ' + file_path + key + '_*_*'
    print cmd
    os.system(cmd)
