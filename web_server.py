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
	msg = '<!DOCTYPE html> \n' + \
		'<html> \n' + \
		'<head> \n' + \
		'<style> \n' + \
		'table, th, td { \n' + \
		'border: 1px solid black; \n' + \
		'border-collapse: collapse; \n' + \
		'}\n' + \
		'th, td { \n' + \
		'padding: 5px; \n' + \
		'} \n' + \
		'</style> \n' + \
		'</head> \n' + \
		'<body> \n'

	msg += '<table style=\"width:10%\"> \n'
	msg += '<tr> \n <th>Task ID</th> \n <th>Progress</th> \n </tr>'
        for fname in os.listdir(basepath):
            path = os.path.join(basepath, fname)
            if os.path.isdir(path):
                continue

            _, ext = os.path.splitext(path)
            if ext == '.pkl':
                pkl_file = open(path, 'rb')
                task = dill.load(pkl_file)
                pkl_file.close()
		msg += '<tr>\n'
		msg += '<td>\n'
		msg += task.task_id + '\n'
		msg += '</td>\n'
		msg += '<td>\n'
		msg += str(task.progress) + '\n'
		msg += '</td>\n'
		msg += '</tr>'
	msg += '</table> \n'
	msg += '</body> \n'
	msg += '</html> \n'
	return msg


application = web.application(urls, globals()).wsgifunc()

