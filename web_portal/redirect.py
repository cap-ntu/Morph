'''
Author: Guanyu Gao
Email: guanyugao@gmail.com
Description:
Web protal for submitting transcoding task and querying task progress.
The users can access via RESTful API.
'''

import os
import web
import json
import subprocess
from random import Random

urls = (
    '/', 'home',
    '/get_progress', 'get_progress',
    '/submit_file', 'submit_file',
    '/submit_url', 'submit_url'
    )

work_path = '/tmp'
cln_path  = '/home/transcoding/client.py'
qry_path  = '/home/transcoding/query.py'

def gen_key(randomlength = 8):
    str     = ''
    chars   = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length  = len(chars) - 1
    random  = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


class submit_file:

    def POST(self):

        upload_file = web.input(video_file = {}, target_resolution = None, priority = None)
        file_name = upload_file['video_file'].filename
        _, ext = os.path.splitext(file_name)

        key = gen_key()
        file_name = os.path.join(work_path, key + ext)
        f = open(file_name, "wb")
        f.write(upload_file['video_file'].value)
        f.close()

        res = upload_file['target_resolution']

        cmd = "python " + cln_path + " -l " + file_name + " -t " + key + " -s " + res
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        ret = p.returncode

        ret = json.dumps({"key": key, "ret": 0})
        return ret


class submit_url:

    def POST(self):
        new_task = web.input(url = None, target_resolution = None, priority = None)
        url = new_task['url']
        res = new_task['target_resolution']

        key = gen_key()
        cmd = "python " + cln_path + " -u " + url + " -t " + key + " -s " + res
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        ret = p.returncode
        ret = json.dumps({"key": key, "ret": 0})

        return ret


class get_progress:

    def POST(self):
        s = web.input(key = None)

        cmd = "python " + qry_path + " -k " + str(s.key)
        web.debug(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        prg = p.returncode

        ret = json.dumps({"key": str(s.key), "ret": str(prg)})
        return ret

class home:
    def GET(self):
        with open('/var/www/Morph/web_portal/home.html', 'r') as homepage:
            data = homepage.read()
            return data

    def POST(self):
        x = web.input(myfile={})
        web.debug(x['myfile'].filename) # This is the filename
        web.debug(x['myfile'].value) # This is the file contents
        web.debug(x['myfile'].file.read()) # Or use a file(-like) object
        raise web.seeother('/')

application = web.application(urls, globals()).wsgifunc()



