import os
import web
import json
from random import Random

urls = (
    '/', 'home',
    '/get_progress', 'get_progress',
    '/submit', 'submit'
    )


def gen_key(randomlength = 8):
    str     = ''
    chars   = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length  = len(chars) - 1
    random  = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


class submit:
    def GET(self):
        return """<html><head></head><body>
            <form method="POST" enctype="multipart/form-data" action="">
            <input type="file" name="video_file" />
            <br/>
            <input type="submit" />
            </form>
            </body></html>"""

    def POST(self):
        upload_file = web.input(video_file = {}, target_resolution = None)
        file_name = upload_file['video_file'].filename
        _, ext = os.path.splitext(file_name)

        key = gen_key()
        file_name = os.path.join('/tmp', key + ext)
        f = open(file_name, "wb")
        f.write(upload_file['video_file'].value)
        f.close()

        res = upload_file['target_resolution']

        ret = json.dumps({"key": key, "ret": 0})
        return res


class get_progress:
    def POST(self):
        s = web.input(key = None)
        return s.key

    def GET(self):
        s = web.input(key = None)
        return s.key


class home:
    def GET(self):
        return "Restful API for Video Transcoding"

application = web.application(urls, globals()).wsgifunc()



