#!/usr/bin/python
import sys
import scipy.io
import numpy as np
import neurolab as nl

input   = scipy.io.loadmat('../data/input.mat')
target  = scipy.io.loadmat('../data/target.mat')
input   = input['input'].transpose()
target  = target['t']

print input.shape
print target.shape
sys.exit()

net = nl.net.newff([[400, 3500], [9, 13000]], [30, 1])
err = net.train(input, target, epochs=500, show=1)

out = net.sim(input)
print out
sys.exit()

for i in range(490):
    print input[i], target[i], '---', out[i]


