# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 16:35:03 2016

@author: qitlab
script to use aomscan.py scanfreq
"""
from aomscan import scanfreq
import numpy as np
import matplotlib.pylab as plt
#cal_data=np.genfromtxt('up_1.txt')
cal_data=np.genfromtxt('d_1.txt')
re=scanfreq(cal_data,0,fixamp=0)
power=np.array(re[2])*1e3
freq = re[0]
amp=re[1]
plt.plot(freq,power,'-o')
fig2=plt.figure()
plt.plot(freq,amp,'-o')