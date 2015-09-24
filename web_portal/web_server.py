'''
A simple web page for listing all of the task id.
'''

import os
import web
import sys
import dill

sys.path.append('/var/www/webpy-app/')
import common

basepath = '/data/master/'

urls = (
    '/.*', 'home_page',)


class home_page:
    def GET(self):
	task_list = []
	render = web.template.render('/var/www/webpy-app/templates/')
	for fname in os.listdir(basepath):
            path = os.path.join(basepath, fname)
            if os.path.isdir(path):
                continue

            _, ext = os.path.splitext(path)
            if ext == '.pkl':
                pkl_file = open(path, 'rb')
                task = dill.load(pkl_file)
                pkl_file.close()
		task_list.append(task)
	return render.home(task_list)


application = web.application(urls, globals()).wsgifunc()

