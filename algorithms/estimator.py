#!/usr/bin/python
import sys
import scipy.io
import numpy as np
import neurolab as nl


input   = scipy.io.loadmat('transcoding1to5.mat')
target  = scipy.io.loadmat('transcoding6.mat')
#i = input['transcoding1to5'].transpose()
i = input['transcoding1to5']
t = target['transcodingdata']

#print target
#print i.shape
#print target.shape
#sys.exit()

norm_t = nl.tool.Norm(t)
t = norm_t(t)

'''
net = nl.net.newff(nl.tool.minmax(i), [20, 1])
err = net.train(i, t, epochs=1000, show=1)
net.save('estimator.net')
'''

net = nl.load('estimator.net')
out = net.sim(i)

out = norm_t.renorm(out)
t = norm_t.renorm(t)

#print target['t'] - out
e = t - out
#print type(e)
#print e.shape
#print len(e)

j = 0
while j < len(e):
    print t[j], '   ', e[j]
    j = j + 1

sys.exit()



