

class MyClass:
    """A simple example class"""
    def __init__(self):
        self.i = 12345

def init():
    a = MyClass()
    print 'a is:'
    print type(a)
    return a

b = init()
print type(b)
print b.i

content = pack + data
print 'content length:', len(content)

sum = 0
while True:
    cnt = s.send(content[sum: sum + 1024*400])
    # print cnt
    sum = cnt + sum
    if cnt == 0:
        print 'finished:', sum
        break

s.shutdown(gevent.socket.SHUT_WR)
