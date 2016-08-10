# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 15:18:47 2016

@author: qitlab
Short script used for scanning probe freq and detect tranmistion through cav with or without atoms

Modified from cav_scan.py for usbmini-counter for the detection method
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
import datetime
import os
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
    return I*(gamma**2)/(((x-b)**2)+(gamma)**2)
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
def fitting(freq2,powers2,std2,p0 = [9000,50,40,4000]):
    #fitting powers2 no atoms
    y2=np.asarray(powers2)
    x2=freq2
    xmax=np.argmax(y2)
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
    lwfit_empty=round((fitresult[1])*2,2)
    detun_empty=round(fitresult[2],2)
    plt.plot(f,powers,'-o')
    plt.plot(f,yfit2)
    print('CHECK ALIGNMENT RESULT:')
    print('Chi_square: ',chi_square)
    print('detunning fitted: ',detun_empty)
    print('FWHM: ',lwfit_empty)
    approval=1
    if chi_square>chi_square_target or detun_empty>(detun_target+10) or detun_empty<(detun_target-10):
        approval=0
        print('Fail the alignment check. Please proceed to the manual prepartion stage')
    return approval
def check_atoms(dds1):
    dds1.set_power(500)
    time.sleep(1)
    (freq,power)=scan_table(table,DDS_address,freq=-80,detector='usbmini-counter',umc_average=10)
    powers=np.mean(power)
    time.sleep(1)
    dds1.set_power(0)
    (freq,power2)=scan_table(table,DDS_address,freq=-80,detector='usbmini-counter',umc_average=10)
    powers2=np.mean(power2)
    print('power with atoms ',powers)
    print('power without atoms ',powers2)
    if powers>(powers2+700):
        approval=1
    else:
        approval=0
        print('Probably no atoms because no significant fluorescence leaked through cavity mirrors')
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
detun=24
#############################################################################






######################
for j in np.linspace(6,7,2):

    (d,p)=scan_table(table,DDS_address,freq=detun,detector='usbmini-counter',directo='test',umc_average=100)
    print('Powers at the selected detunning is ',p)
    time.sleep(5)
    message=lock_request()
    print(message)

    #Check alignment
    detun_target=25
    chi_square_target=40
    print('Start checking alignment')
    approval1=check_alignment(detun_target,chi_square_target)
    print('Finish checking alignment')
    #Check atoms
    print('Start checking atoms')
    approval2=check_atoms(dds1)
    print('Finish checking atoms')
    if (approval1*approval2==0):
        print('Fail either one of the tests')
        print('Stopping the experiment')
        sys.exit()
    scan_table(table,DDS_address,freq=detun,detector='usbmini-counter',directo='test',umc_average=10)
    message=lock_request()
    print(message)
    print('')
    print('Congratz. Passed the tests')
    print('Running experiment')

    j=int(j)
    print('iteration ',j)
    main_directo='nsplit/s'+str(j)
    #for atoms
    powers=[]
    std=[]
    #for wo atoms
    powers2=[]
    std2=[]
    #for fix f wo atoms
    powers3=[]
    std3=[]
    for i in f:

        dds1.set_power(500)
        time.sleep(1)

        (freq,power)=scan_table(table,DDS_address,freq=i,detector='usbmini-counter',umc_average=500)
        std.append(np.std(power))
        powers.append(np.mean(power))
        #print('Freq Power:',freq,powers)
        dds1.set_power(0)
        time.sleep(2)

        (freq,power2)=scan_table(table,DDS_address,freq=i,detector='usbmini-counter',umc_average=10)
        std2.append(np.std(power2))
        powers2.append(np.mean(power2))
        #print('Freq Power:',freq,powers)
        time.sleep(1)

        (freq,power3)=scan_table(table,DDS_address,freq=detun,detector='usbmini-counter',umc_average=5)
        std3.append(np.std(power3))
        powers3.append(np.mean(power3))
        time.sleep(1)

        message=lock_request()
        print('\n')
        print(message)
        print('\n')
#####################################3
#Saving data part
    currentdate = str(datetime.date.today()).split('-')
    year = currentdate[0]
    month = currentdate[1]
    day =  currentdate[2]
    base_folder='/home/qitlab/data/usbminicounter/nsplit'
    directory = base_folder + '/'+ year + '/'  + month + '/' + day  + '/'
    tar_path=directory+'s'+str(j)+'.dat'
    print(tar_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    w=np.column_stack((f,powers,std,powers2,std2,powers3,std3))

    np.savetxt(tar_path,w)
   # np.savetxt(tar_path2,woatoms)
    #np.savetxt(tar_path3,woatomfixf)
