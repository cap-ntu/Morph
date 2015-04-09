import os

file_name = ''
file_path = ''

f = open(file_name)
lines = f.readlines()

for line in lines:
    cmd = 'rm -f ' + key + '_*_*'
    os.system(cmd)
