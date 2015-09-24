'''
Tran the neural network and evaluate the performance of the transcoding time estimation
'''

#!/usr/bin/python
import sys
import scipy.io
import numpy as np
import neurolab as nl

#the input feature vectors of each training instance
input   = scipy.io.loadmat('t3_input.mat')
#the real transcoding time of each training instance
target  = scipy.io.loadmat('t3_output.mat')

#i = input['transcoding1to5'].transpose()
i = input['t3_input']
t = target['t3_output']

#print target
#print i.shape
#print target.shape
#sys.exit()

norm_t = nl.tool.Norm(t)
t = norm_t(t)

#train and save the neural network
'''
net = nl.net.newff(nl.tool.minmax(i), [10, 1])
err = net.train(i, t, epochs=1000, show=1)
net.save('t3_estimator.net')
'''

#load the neural network for transcoding time estimation
net = nl.load('t3_estimator.net')

#test the input using the neural network
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



