#!/usr/bin/python

import scipy.io
import numpy as np
import neurolab as nl

input   = scipy.io.loadmat('../data/input.mat')
target  = scipy.io.loadmat('../data/target.mat')
input   = input['input'].transpose()
target  = target['t']

print input.shape
print target.shape

net = nl.net.newff([[400, 3500], [9, 13000]], [20, 1])
err = net.train(input, target, show=1)

#net.sim([[0.2, 0.1]])


