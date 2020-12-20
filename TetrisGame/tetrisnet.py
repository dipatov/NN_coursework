import torch
import numpy as np
from torch import nn

class TetrisNet ():
    def __init__(self):
        super(TetrisNet, self).__init__()
        self.m1 = np.array([])
        self.bias1 = np.array([])
        self.m2 = np.array([])
        self.bias2 = np.array([])
        
    def forward(self, x):
        x = x.dot(self.m1)
        x += self.bias1
        for i in range(len(x[0])):
            x[0, i] = max(x[0,i], 0.)
        x = x.dot(self.m2)
        x += self.bias2
        return x[0][0]