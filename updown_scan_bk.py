# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 14:20:56 2016

@author: NgChiHuan
"""

from CQTdevices import DDSComm, PowerMeterComm, WindFreakUsb2
import matplotlib.pylab as plt
import numpy as np
import time

def setdds(table,channel,device,freq=180,fixamp=50):
    DDS_address = device
    DDS_channel = channel
    if fixamp==0:
        i=np.where(table[:,0]==freq)[0][0]
        print(i)
        amp=table[i,1]
    else:
        amp=fixamp
    dds = DDSComm(DDS_address,DDS_channel)
    print(amp)
    dds.set_freq(freq)
    dds.set_power(int(amp))
    return (amp)
def scanprobe_logic(freq,tableup,tabledown,device,fixamp=50):
    datup=np.genfromtxt(tableup)
    datdown=np.genfromtxt(tabledown)
    
    f_up=datup[:,0]
    amp_up=datup[:,1]
    l_up=len(f_up)
    
    f_down=datdown[:,0]
    amp_down=datdown[:,1]
    l_down=len(f_down)    
    
    step=2
    maxf=2*(f_up[l_up-1]-f_down[0])
    minf=2*(f_up[0]-f_down[l_down-1])
    ifreq=175#init f
    if (freq>0):
        if ((freq/2)%2==0):
            f_down=ifreq-freq/4
            f_up=ifreq+freq/4
            
        else:
           f_down=ifreq
          
           f_up=freq/2+ifreq
           
    elif freq<0:
         if ((freq/2)%2==0):
            f_down=ifreq+freq/4
            f_up=ifreq-freq/4
            
         else:
           f_up=ifreq
           f_down=freq/2+ifreq
           
    else:
           f_up=ifreq
           f_down=ifreq
    ampd=setdds(datdown,0,device,freq=f_down,fixamp=fixamp)
    ampu=setdds(datup,1,device,freq=f_up,fixamp=fixamp)
    print('fup fdown ampup ampdown')
    print(f_up, f_down,ampu,ampd)
def scanprobe_updown(fs,fst,device,tableup,tabledown,step=2,fixrfp=False):
    Power_meter_address = '/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Optical_Power_Meter_OPM-QO04-if00'
    pm = PowerMeterComm(Power_meter_address)
    pm.set_range(2)
    freq=np.arange(fs,fst,step)
    average=50
    wavelength=780
    powers_adj=[]
    powers=[]
    for i in range(len(freq)):
        scanprobe_logic(freq[i],tableup,tabledown,device,fixamp=0)#adjust power for compensation
        #wind.set_freq(freq_range[i])
        value = []
        time.sleep(1)
        p=0
        for m in range(average):
            power = pm.get_power(wavelength)
            value.append(power)
            time.sleep(1e-3) # delay between asking for next value
        p=np.mean(value)
        powers_adj.append(p)
        if fixrfp==True:
            scanprobe_logic(freq[i],tableup,tabledown,device,fixamp=180)
            value = []
            time.sleep(0.1)
            p=0
            for m in range(average):
                power = pm.get_power(wavelength)
                value.append(power)
                time.sleep(1e-3) # delay between asking for next value
            p=np.mean(value)
            powers.append(p)
            
    return (freq,np.array(powers)*1e6,np.array(powers_adj)*1e6)
if __name__=='__main__':
    DDS_address = '/dev/ioboards/dds_QO0037'
    DDS_channel = 1
    tableup=('up_1.txt')
    tabledown=('d_1.txt')
    dtup=np.genfromtxt(tableup)
    dtd=np.genfromtxt(tabledown)
    freq=[]
    powers=[]
    powers_adj=[]
    #scanprobe_logic(0,tableup,tabledown,DDS_address,fixamp=0)#adjust power for compensation
    (freq,powers,powers_adj)=scanprobe_updown(-100,100,DDS_address,tableup,tabledown,step=4)
    plt.plot(freq,powers,'-o')
    plt.plot(freq,powers_adj,'-o',color='red')
    plt.show()
    #a=setdds(dtd,0,DDS_address,freq=200,fixamp=0)
    #print(a)
    