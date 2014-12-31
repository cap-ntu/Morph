
f = open('video.list')
lines = f.readlines()
f.close()

video_list = []

for line in lines:
    line = line.replace('\n', '')
    video_list.append(line)

cmd = 'ffmpeg -f concat -i ' + list_path + ' -c copy ' + new_file
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
stdout, stderr = p.communicate()
ret = p.returncode
