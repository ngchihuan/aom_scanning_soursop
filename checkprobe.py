# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import time
from CQTdevices import AnalogComm, DDSComm
from updown_scan_1_2_1 import *
import numpy as np
analogpm_add='/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Analog_Mini_IO_Unit_MIO-QO13-if00' # Channel 1
a=AnalogComm(analogpm_add)
DDS_address = '/dev/ioboards/dds_QO0037'
i = 0
average=10
min_val = -96
max_val = 96
space = 6
data_points= (max_val - min_val) / space + 1
f=np.linspace(min_val,max_val,data_points)
powers=[]
stds=[]
table=np.genfromtxt('calibrated_table_2.txt')

for i in f:
    scan_table(table,DDS_address,freq=i,detector='usbmini-counter',directo='test',duration=1)
    power=[]
    time.sleep(2)
    for j in range(average):        
        power.append(float(a.get_voltage(0)))
        time.sleep(1)
    powers.append(np.mean(power))
    print(powers)
    stds.append(np.std(power))
data=np.column_stack((powers,stds))
np.savetxt('checkprobe_15_aug.dat',data)
dds1=DDSComm(DDS_address,0)
dds1.off()
bg=0
bg_std = 0
power=[]
for j in range(average):        
    power.append(float(a.get_voltage(0)))
bg=np.mean(power)
bg_std=np.std(power)
print(bg,bg_std)

    