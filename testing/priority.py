import Queue
from Queue import PriorityQueue


queue = PriorityQueue(maxsize = 100)
queue.put((1, 1, "item 1"))
queue.put((1, 1, "item 2"))
queue.put((1, 1, "item 3"))
queue.put((1, 1, "item 3"))

print queue.get()
print queue.get()
print queue.get()
try:
    2 /0
    print queue.get_nowait()
except Queue.Empty:
    print "empty"
except ZeroDivisionError:
    print 'zero'
except:
    print 'other'
