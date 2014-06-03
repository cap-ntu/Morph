
from SocketServer import ThreadingMixIn
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

class TXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer): pass


def add(a, b):
    print 'hello1'
    while 1:
        pass
    return a + b

def gen(n):
    print 'hello2'
    while 1:
        pass
    return 2 * n

#create server
server = TXMLRPCServer(('', 8080), SimpleXMLRPCRequestHandler)
server.register_function(add, "add")
server.register_function(gen, "gen")
server.serve_forever()
