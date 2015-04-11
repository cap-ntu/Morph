import web

urls = (
    '/.*', 'hello',)

class hello:
    def GET(self):
        return "Hello, world."


application = web.application(urls, globals()).wsgifunc()

