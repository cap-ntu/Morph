import web

basepath = '/data/master/'

urls = (
    '/.*', 'home_page',)

class home_page:
    def GET(self):
        for fname in os.listdir(basepath):
            path = os.path.join(basepath, fname)
            if os.path.isdir(path):
                continue

            _, ext = os.path.splitext(path)
            if ext == '.pkl':
                info = c.probe(path)


application = web.application(urls, globals()).wsgifunc()

