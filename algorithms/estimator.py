#!/usr/bin/python
import sys
import scipy.io
import numpy as np
import neurolab as nl

input   = scipy.io.loadmat('input.mat')
target  = scipy.io.loadmat('target.mat')
i = input['input'].transpose()
t = target['t']

'''
print target
print input.shape
print target.shape
sys.exit()
'''

norm_t = nl.tool.Norm(t)
t = norm_t(t)

net = nl.net.newff(nl.tool.minmax(i), [10, 1])
err = net.train(i, t, epochs=500, show=1)

out = net.sim(i)
out = norm_t.renorm(out)

print target['t'] - out
sys.exit()



