# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 15:18:47 2016

@author: qitlab
Short script used for scanning probe freq and detect tranmistion through cav with or without atoms
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
DDS_address = '/dev/ioboards/dds_QO0037'
min_val = -96
max_val = 96
space = 6
data_points= (max_val - min_val) / space + 1
f=np.linspace(min_val,max_val,data_points)
table=np.genfromtxt('calibrated_table.txt')
print(f)
#test
#scan_table(table,DDS_address,freq=None,detector='pm',directo='probescan/withatom')
#scan_table(table,DDS_address,freq=0,detector='pm',directo='test')
'''
i=0
while (True):
    scan_table(table,DDS_address,freq=0,detector='apd',directo='test',duration=1)
    i=i+1
    print(i)
'''

DDS_address1 = '/dev/ioboards/dds_QO0019'
DDS_channel1 =0
dds1 = DDSComm(DDS_address1,DDS_channel1)
def review(f1):
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
i=0
scan_table(table,DDS_address,freq=0,detector='apd',directo='test_transverselock',duration=10)
while i<1000:
    #message=lock_request()
    #print(message)
    
    while True:
        f2=scan_table(table,DDS_address,freq=0,detector='apd',directo='test_notransverselock',duration=1)
        a=review(f2)
        if a==0:
            break
    time.sleep(2)
'''
for i in f:
    
    message=lock_request()
    print(message)
    dds1.set_power(500)
    time.sleep(1)
    while True:
        f1=scan_table(table,DDS_address,freq=i,detector='apd',directo='nsplit/s3/withatom',duration=10)
        a=review(f1)
        if a==0:
            break
    dds1.set_power(0)
    time.sleep(2)
    while True:
        f2=scan_table(table,DDS_address,freq=i,detector='apd',directo='nsplit/s3/woatom',duration=3)
        a=review(f2)
        if a==0:
            break
    
    time.sleep(1)
    while True:
        f3=scan_table(table,DDS_address,freq=0,detector='apd',directo='nsplit/s3/woatomfixf',duration=1)
        a=review(f3)
        if a==0:
            break
    time.sleep(1)
'''