# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 15:18:47 2016

@author: qitlab
Stability of cavity via continous measurement of cavity spectrum

NOT YET IMPLEMENTED: standard errors of the fitted parameters
"""

from CQTdevices import DDSComm, PowerMeterComm, WindFreakUsb2
#import matplotlib.pylab as plt
import numpy as np
import time
import timestampcontrol as tsc
from updown_scan_1_2_1 import *
import subprocess as sp
from subprocess import check_output, STDOUT, CalledProcessError
from hameg_control_v2 import Hameg

#zmq is a package for the communication between 2 programs
import zmq

import matplotlib.pyplot as plt
from scipy.optimize import leastsq
context = zmq.Context()

def lock_request():
    '''
    to send request to transverse lock program (retreat v1.1)
    '''
    ##init communication
    print ("Connecting to the retreat controller server")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")
    print ("Sending request to lock")
    socket.send(b"Please Lock")

    #  Get the reply.
    message = socket.recv()
    print ("Received reply : ", message )
    return message
#fitting
def line_model(x,I,gamma,b,C):
    return I*(gamma**2)/(((x-b)**2)+(gamma)**2) + C
#have 3 parameters for the fit (I,gamma,b,C)
#I is the maximum intensity
#gamma is 1/2lw
#b is argmax
#C is offset[1000:8000]
#I,b are fixedmaxp-1000:maxp+2000
def line_func(p, y, x):
    I,gamma,b,C = p
    err = y - line_model(x,I,gamma,b,C)
    return err

def line_eval(x, p):
    I,gamma,b,C = p
    return line_model(x,I,gamma,b,C)
def fitting(freq,powers):
    y=np.asarray(powers)
    x=freq
    xmax=20
    p0 = [16000,80,xmax,0]
    plsq = leastsq(line_func, p0, args=(y,x),full_output=1)
    fitresult=plsq[0]
    infodict=plsq[2]
    lwfit=(fitresult[1])*2
    detun=fitresult[2]
    ss_err=(infodict['fvec']**2).sum()
    ss_tot=((y-y.mean())**2).sum()
    rsquared=1-(ss_err/ss_tot)
    print('Fitted parameters: detun, lw, rsquare:',detun,lwfit,rsquared)
    return(detun,lwfit,rsquared)

#####################
DDS_address = '/dev/ioboards/dds_QO0037'
min_val = 96
max_val = -96
space = -6
data_points= (max_val - min_val) / space + 1
f=np.linspace(min_val,max_val,data_points)
table=np.genfromtxt('calibrated_table.txt')
print(f)
#start the scanning
detuna=[]
lwfita=[]
rsquareda=[]
maxa=[]#maximum of scav
scan_table(table,DDS_address,freq=0,detector='usbmini-counter',directo='test',duration=1)
t0 = time.time()
dat=[]#to save all spectrum scans
dat_fit=[]#to save fitting parameters of spectrum scan
for j in range(20):#repeat spectrum scanning
    power=0
    powers=[]
    print('iteration:',j)
    for i in f:
        print(i)
        '''
        scan_table(table,DDS_address,freq=0,detector='usbmini-counter',directo='test',duration=1)
        message=lock_request()
        print(message)
        '''
        (freqsinglevalue,power)=scan_table(table,DDS_address,freq=i,detector='usbmini-counter',directo='test',duration=1)
        print('counts:',power)
        
        powers.append(power)
    plt.plot(f,powers)
    (detun,lwfit,rsquared)=fitting(f,powers)
    dat.append(powers)
    maxa.append(np.max(powers))
    detuna.append(detun)
    lwfita.append(lwfit)
    rsquareda.append(rsquared)
dat_fit=np.column_stack((detuna,lwfita,maxa,rsquareda))

np.savetxt('stability_test_wotl_dat'+str(time.strftime("%H:%M:%S"))+'.dat',dat)
np.savetxt('stability_test_wotl_datfit'+time.strftime("%H:%M:%S"),dat_fit)
print('Measurement take in (s) ',time.time()-t0)