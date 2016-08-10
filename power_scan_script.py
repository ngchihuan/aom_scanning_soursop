# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 17:05:41 2016

@author: qitlab
"""
import power_calibration_up
from power_calibration_up import power_scan
import imp
import matplotlib.pylab as plt
import numpy as np
imp.reload(power_calibration_up)
start = 150
stop = 201
step = 1

freq_range = np.arange(start,stop,step)
#cal_data=np.genfromtxt('up_1.txt')
cal_data=np.genfromtxt('aftfb_corrected_down_2.txt')
# set starting power make it low to ensure have enough adjustment when far from AOM resonance
re=power_scan(freq_range,target_power=0.06/1000,cf=True,cal_data=[],initset_power=50,k1=5e5)
powers_adj=[]
powers = re[1]#run scan should take about a minute with 10 averages
powers_adj = re[0]
setpower= re[2]
setpower_track=re[3]
powers_track=re[4]
plt.plot(freq_range,powers,'-o')#plot data to make sure it makes sense
plt.plot(freq_range,powers_adj,'-o',color='red')#plot data to make sure it makes sense

plt.xlabel('Frequency (MHz)')
plt.ylabel('Power (mW)')
plt.show()
fig2=plt.figure()
plt.plot(freq_range,setpower,'-o',color='black')#plot data to make sure it makes sense1
plt.show()