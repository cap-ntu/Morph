'''
Author: Guanyu Gao
Email: guanyugao@gmail.com
Description:
Web portal for submitting transcoding task and querying task progress.
The users can access via RESTful API.
'''

import os
import web
import json
import time
import datetime
import subprocess
from random import Random
import config

urls = (
    '/', 'home',
    '/get_progress',         'get_progress',
    '/rest_submit_file',     'rest_submit_file',
    '/rest_submit_url',      'rest_submit_url',
    '/rest_get_progress',    'rest_get_progress',
    '/get_result',           'get_result',
    '/get_tgt_files',        'get_tgt_files',
    '/download',             'download',
    '/instance',             'instance',
    '/task',                 'task',
    '/view_video',           'view_video'
    )

morph_path = os.path.realpath('..')
dir_path = os.path.realpath('.')
work_path = os.path.join(morph_path, 'tmp/')
cln_path = os.path.join(morph_path, 'cli_submit.py')
qry_path = os.path.join(morph_path, 'cli_query.py')
tmpt_path = os.path.join(dir_path, 'templates/')

'''
generate a random key for the task
'''
def gen_key(randomlength = 8):
    str     = ''
    chars   = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length  = len(chars) - 1
    random  = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

def ts_to_date(ts):
    if ts <= 0:
        return "unavailable"
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st

'''
start a transcoding operation
'''
def start_transcoding(file_name, key, res):
    cmd = "python " + cln_path + " -l " + file_name + " -t " + key + " -s " + res
    web.debug(cmd)
    os.chdir(morph_path)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    ret = p.returncode
    web.debug(stdout)
    web.debug(stderr)
    return ret

'''
save the uploaded video file
'''
def save_file(upload_file, key):
    file_name = upload_file['video_file'].filename
    _, ext = os.path.splitext(file_name)
    file_name = os.path.join(work_path, key + ext)
    f = open(file_name, "wb")
    f.write(upload_file['video_file'].value)
    f.close()
    return file_name

'''
The restful API interface for submitting a video file
'''
class rest_submit_file:
    def POST(self):
        upload_file = web.input(video_file={}, target_resolution=None, priority=None)
        key = gen_key()
        res = upload_file['target_resolution']
        file_name = save_file(upload_file, key)
        ret = start_transcoding(file_name, key, res)
        ret = json.dumps({"key": key, "ret": ret})
        return ret

class rest_submit_url:
    def POST(self):
        new_task = web.input(url=None, target_resolution=None, priority=None)
        url = new_task['url']
        res = new_task['target_resolution']

        key = gen_key()
        cmd = "python " + cln_path + " -u " + url + " -t " + key + " -s " + res
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        ret = p.returncode
        ret = json.dumps({"key": key, "ret": 0})

        return ret

class rest_get_progress:
    def POST(self):
        s = web.input(key=None)
        os.chdir(morph_path)
        cmd = "python " + qry_path + " -k " + str(s.key)
        web.debug(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        prg = p.returncode
        ret = json.dumps({"key": str(s.key), "ret": str(prg)})
        return ret

'''
Get the transcoding progress
'''
class get_progress:
    def POST(self):
        data = web.data()
        web.debug(data)
        (_, key) = data.split('=')
        os.chdir(morph_path)
        cmd = "python " + qry_path + " -k " + key
        web.debug(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        prg = p.returncode
        web.debug(stdout)
        return str(prg)

'''
The home page for the Demo
'''
class home:
    def GET(self):
        render = web.template.render(tmpt_path, base='layout')
        return render.home()

    def POST(self):
        x = web.input(video_file={}, p_240=None, p_360=None, \
                      p_480=None, p_720=None)
        key = gen_key()
        file_name = save_file(x, key)
        res = ''
        if x['p_240'] == '240':
            res += '426x240 '
        if x['p_360'] == '360':
            res += '640x360 '
        if x['p_480'] == '480':
            res += '854x480 '
        if x['p_720'] == '720':
            res += '1280x720 '
        ret = start_transcoding(file_name, key, res)
        state = ''
        if ret == 0:
            state = 'successful'
        else:
            state = 'failed'
        other_page = "get_result?" + "key=" + key + "&" + \
                     "res=" + res + '&' + \
                     "state=" + state
        raise web.seeother(other_page)

class get_result:
    def GET(self):
        data = web.input(res=None, state=None, key=None)
        web.debug(data)
        render = web.template.render(tmpt_path, base='layout')
        return render.result(data.key, data.state, data.res)

def gen_dl_links(key):
    os.chdir(morph_path)
    cmd = "python " + qry_path + " -k " + key
    web.debug(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    web.debug(stdout)
    prg = p.returncode
    if prg == 100:
        f = stdout.split('\'')
        ret = '<h2>Transcoded video files</h2>' + '<pre><code>'
        for i in f:
            if i.find('Morph') < 0:
                continue
            ret += i.replace('/var/www', 'http://155.69.146.43') + '<br>'
        ret += '</code></pre>'
        web.debug(ret)
        return ret
    if prg != 100:
        web.debug(prg)
        ret = '<h2>Warning</h2>' + '<pre><code>'
        if prg == (-100 & 255):
            ret += "key format error" + '<br>'
        if prg == (-10 & 255):
            ret += "invalidated key" + '<br>'
        if prg >= 0 and prg < 100:
            ret += "in progress, waiting..." + '<br>'
        ret += '</code></pre>'
        return ret

class get_tgt_files:
    def POST(self):
        data = web.data()
        web.debug(data)
        (_, key) = data.split('=')
        res = gen_dl_links(key)
        return res

class instance:
    def GET(self):
        db = web.database(dbn='mysql', db=config.mysql_db_name, user=config.mysql_user_name, pw=config.mysql_password)
        res = db.query("SELECT * FROM server_info")
        data = ""
        cur_t = time.time()
        state = ['sleep', 'active']
        for i in res:
            data += "<tr>"
            data += "<td>" + str(i.id) + "</td>"
            data += "<td>" + str(format(cur_t - i.last_time, '.2f')) + ' seconds ago' + "</td>"
            data += "<td>" + state[i.state] + "</td>"
            data += "</tr>"
        render = web.template.render(tmpt_path, base='layout')
        return render.instance_info(data)

class download:
    def GET(self):
        render = web.template.render(tmpt_path, base='layout')
        return render.download("")

    def POST(self):
        data = web.data()
        (_, tmp_key) = data.split('=')
        web.debug(tmp_key)
        key = ""
        for s in tmp_key:
            if s.isdigit() or s.isalpha():
                key += s
        if len(key) == 0:
            render = web.template.render(tmpt_path, base='layout')
            return render.download("")
        else:
            res = gen_dl_links(key)
            render = web.template.render(tmpt_path, base='layout')
            return render.download(res)

class task:
    def GET(self):
        db = web.database(dbn='mysql', db=config.mysql_db_name, user=config.mysql_user_name, pw=config.mysql_password)
        res = db.query("SELECT * FROM task_info")
        data = ""
        state_code = {0: 'finished', 1: 'in progress', -3: 'merge error', \
                      -2: 'block error', -1: 'split error'}
        for i in res:
            data += "<tr>"
            data += "<td>" + str(i.id) + "</td>"
            data += "<td>" + ts_to_date(i.submit_time) + "</td>"
            data += "<td>" + ts_to_date(i.start_time) + "</td>"
            data += "<td>" + ts_to_date(i.finish_time) + "</td>"
            data += "<td>" + state_code[i.task_ongoing] + "</td>"
            data += "</tr>"
        render = web.template.render(tmpt_path, base='layout')
        return render.task_info(data)

def gen_formats(key):
    os.chdir(morph_path)
    cmd = "python " + qry_path + " -k " + key
    web.debug(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    web.debug(stdout)
    prg = p.returncode
    ret = []
    if prg == 100:
        f = stdout.split('\'')
        for i in f:
            if i.find('morph') < 0:
                continue
            ret.append(i.replace('/var/www', 'http://155.69.146.43'))
        return ret
    else:
        return ret

class view_video:
    def GET(self):
        render = web.template.render(tmpt_path, base='layout')
        return render.view_video("")

    def POST(self):
        data = web.data()
        (_, tmp_key) = data.split('=')
        web.debug(tmp_key)
        key = ""
        for s in tmp_key:
            if s.isdigit() or s.isalpha():
                key += s
        if len(key) == 0:
            render = web.template.render(tmpt_path, base='layout')
            return render.view_video("")
        else:
            res = gen_formats(key)
            if len(res) == 0:
                ret = '<h2>Warning</h2>' + '<pre><code>'
                ret += "No available video" + '<br>'
                ret += '</code></pre>'
                render = web.template.render(tmpt_path, base='layout')
                return render.view_video(ret)
            else:
                ret = '<h2>Enjoy it!</h2> <br><br>'
                for r in res:
                    tmp = r.split('_')
                    tmp = tmp[len(tmp) - 1].replace('.mp4', '')
                    w, h = tmp.split('x')
                    ret += "<video width=\"" + w + "\" height=\"" + h + "\" controls>"
                    ret += "<source src=\"" + r + "\" type=\"video/mp4\">"
                    ret += "</video>"
                    ret += "<br><br><br>"
                render = web.template.render(tmpt_path, base='layout')
                return render.view_video(ret)


'''
the main program for wsgi
'''
application = web.application(urls, globals())
if __name__ == "__main__":
    web.httpserver.runsimple(application.wsgifunc(), ("127.0.0.1", 8888))
