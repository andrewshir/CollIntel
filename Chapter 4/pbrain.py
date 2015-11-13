__author__ = 'Andrew'

from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.structure import TanhLayer
from pybrain.supervised.trainers import BackpropTrainer


wWorld,wRiver,wBank = 101, 102, 103
uWorldBank,uRiver,uEarth = 201, 202, 203
allwords = [wWorld,wRiver,wBank]
allurls=[uWorldBank,uRiver,uEarth]


net = buildNetwork(3, 3, 3, hiddenclass=TanhLayer)
ds = SupervisedDataSet(3, 3)
ds.addSample((1, 0, 1), (1, 0, 0))
ds.addSample((0, 1, 1), (0, 1, 0))
ds.addSample((1, 0, 0), (0, 0, 1))
trainer = BackpropTrainer(net, ds)
errors = trainer.trainUntilConvergence()
print "Erros", errors
resp = net.activate((0,0,1))
print "Bank response", resp

# # XOR sample
# net = buildNetwork(2, 5, 1, bias=True)
# ds = SupervisedDataSet(2, 1)
# ds.addSample([0, 0], [0])
# ds.addSample([0, 1], [1])
# ds.addSample([1, 0], [1])
# ds.addSample([1, 1], [0])
# trainer = BackpropTrainer(net, ds)
# errors = trainer.trainUntilConvergence()
# print "Erros", errors
# resp = net.activate((1,1))
# print "XOR respone (1,0)", resp
# resp = net.activate((0,0))
# print "XOR respone (1,0)", resp
# resp = net.activate((1,0))
# print "XOR respone (0,1)", resp
# resp = net.activate((0,1))
# print "XOR respone (0,1)", resp









