# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 15:18:47 2016

@author: qitlab
Short script used for scanning probe freq and detect tranmistion through cav with or without atoms
"""

from CQTdevices import DDSComm, PowerMeterComm, WindFreakUsb2
import matplotlib.pyplot as plt
import sys
import numpy as np
import time
import timestampcontrol as tsc
from updown_scan_1_2_1 import *
import subprocess as sp
from subprocess import check_output, STDOUT, CalledProcessError
from hameg_control_v2 import Hameg
#zmq is a package for the communication between 2 programs
import zmq
from scipy.optimize import leastsq
context = zmq.Context()
#analogpm_add='/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Analog_Mini_IO_Unit_MIO-QO13-if00'
#apm=AnalogComm(analogpm_add)
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
#######################################################################################################

'''
i=0
while (True):
    scan_table(table,DDS_address,freq=0,detector='apd',directo='test',duration=1)
    i=i+1
    print(i)
'''
#fitting methods
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
def fitting(freq2,powers2,std2,p0 = [2500,50,40,0]):
    #fitting powers2 no atoms
    y2=np.asarray(powers2)
    x2=freq2

    plsq = leastsq(line_func, p0, args=(y2,x2),full_output=1)
    xfit=x2
    yfit2 = (line_eval(xfit,plsq[0]))

    fitresult2=plsq[0]

    blah = np.square(y2 - yfit2) / np.square(np.asarray(std2))
    chi_square2 = round(blah.sum() / (np.size(y2)-4),2)



    return(fitresult2,chi_square2,x2,yfit2)
###########################################################################3

def review(f1):
    '''
    To switch on/off timestamp device in case of fail connection
    '''
    hameg_port="/dev/serial/by-id/usb-HAMEG_HAMEG_HO720_013105245-if00-port0"
    ha=Hameg(hameg_port)
    cmd="du -h "+f1
    o1=sp.check_output(cmd,stderr=STDOUT,shell=True).decode('utf-8').split()
    print(o1[0])
    if o1[0]!='0':
        return 0
    else:
        ha.output_off(2)
        time.sleep(5)
        ha.output_on(2)
        time.sleep(5)
        return 1
def check_alignment(detun_target,chi_square_target):
    DDS_address = '/dev/ioboards/dds_QO0037'
    min_val = 90
    max_val = -90
    space = -10
    data_points= (max_val - min_val) / space + 1
    f=np.linspace(min_val,max_val,data_points)
    table=np.genfromtxt('calibrated_table.txt')
    powers=[]
    std=[]
    for i in f:
        print(i)
        '''
        scan_table(table,DDS_address,freq=0,detector='usbmini-counter',directo='test',duration=1)
        message=lock_request()
        print(message)
        '''
        (freq,power)=scan_table(table,DDS_address,freq=i,detector='usbmini-counter',directo='test',duration=1)
        #print('counts:',power)

        std.append(np.std(power))
        powers.append(np.mean(power))

    (fitresult,chi_square,x2,yfit2)=fitting(f,powers,std)
    plt.plot(f,powers,'-o')
    plt.plot(x2,yfit2)
    lwfit_empty=round((fitresult[1])*2,2)
    detun_empty=round(fitresult[2],2)
    print('CHECK ALIGNMENT RESULT:')
    print('Chi_square: ',chi_square)
    print('detunning fitted: ',detun_empty)
    print('FWHM: ',lwfit_empty)
    approval=1
    if chi_square>chi_square_target or detun_empty>(detun_target+10) or detun_empty<(detun_target-10):
        approval=0
        print('Fail the alignment check. Please proceed to the manual prepartion stage')
    print(fitresult)
    return approval

##############################################################################
#DECLARE EXP PARAMETERS
DDS_address1 = '/dev/ioboards/dds_QO0019'
DDS_channel1 =0
dds1 = DDSComm(DDS_address1,DDS_channel1)
DDS_address = '/dev/ioboards/dds_QO0037'
min_val = -96
max_val = 96
space = 6
data_points= (max_val - min_val) / space + 1
f=np.linspace(min_val,max_val,data_points)
table=np.genfromtxt('calibrated_table.txt')
print(f)
#############################################################################

#scan_table(table,DDS_address,freq=0,detector='apd',directo='test',duration=15)
#message=lock_request()
#print(message)
#print ("GET READY")
#Check alignment
detun_target=30
chi_square_target=10
approval=check_alignment(detun_target,chi_square_target)
if approval==0:
    print('Stopping the experiment')


#scan_table(table,DDS_address,freq=0,detector='apd',directo='test',duration=15)
#message=lock_request()
#print(message)
###############
'''
for j in np.linspace(20,22,3):
    j=int(j)
    print('iteration ',j)
    main_directo='nsplit/s'+str(j)


    for i in f:

        dds1.set_power(500)
        time.sleep(1)
        while True:
            f1=scan_table(table,DDS_address,freq=i,detector='apd',directo=main_directo+'/withatom',duration=10)
            a=review(f1)
            if a==0:
                break
        dds1.set_power(0)
        time.sleep(2)
        while True:
            f2=scan_table(table,DDS_address,freq=i,detector='apd',directo=main_directo+'/woatom',duration=3)
            a=review(f2)
            if a==0:
                break

        time.sleep(1)
        while True:
            f3=scan_table(table,DDS_address,freq=0,detector='apd',directo=main_directo+'/woatomfixf',duration=1)
            a=review(f3)
            if a==0:
                break
        time.sleep(1)
        message=lock_request()
        print(message)
'''
