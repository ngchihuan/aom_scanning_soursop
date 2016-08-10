# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:41:43 2015

RF Power Adjustment Algorithm for AOM

VERSION: 1.1

AUTHOR: CHI HUAN

USAGE:  Scanning aom and measure optical power 
        
        Able to correct non-uniform optical power due to the misalignment coupling into fibre 
        by adjusting rf power into aom

SOFTWARE ARCHITECTURE: 

COMMANDS:   To scan aom freq and measure optical power without adjustment
            aom_scan(freq_range)
            
            To scan aom freq and measure optical power with a calibrated rf power
            aom_scan(cal_data=calibrated data under a form of array)
            
            To run the adjustment mode 1st time without precalibrated values:
            aom_scan(freq_range=,*all the parameters,cf=True)
            
            To run the adjustment mode 1st time without precalibrated values:
            aom_scan(cal_data=,cf=True)

OUTPUT:     (freq_range,np.array(powers_adj)*1000.0,np.array(powers)*1000,setpower,setpower_track,powers_track)
            freq: scanning freq
            powers_adj: optical power detected after adjustment algorithm
            pwoer: bare optical power without adjustment
            setpower: rf power set to aom by the adjustment algorithm
            
REMARK:     Using ADC optical power meter.Pay attention to the power_range of the
            power meter.
"""

from CQTdevices import DDSComm, PowerMeterComm, WindFreakUsb2
import matplotlib.pylab as plt
import numpy as np
import time



# location of devices
#Power_meter_address = '/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Optical_Power_Meter_OPM-QO04-if00'

DDS_address = '/dev/ioboards/dds_QO0037'
DDS_channel = 0
dds = DDSComm(DDS_address,DDS_channel)
#Connect to devices and create objects
#wind = WindFreakUsb2('/dev/serial/by-id/usb-Windfreak_Synth_Windfreak_CDC_Serial_014571-if00')
#Frequency range to scan in MHz
start = 150
stop = 201
step = 1
freq_range = np.arange(start,stop,step)
wavelength=780
init_power=100
init_freq=180


initset_power=150
dds.set_power(initset_power)
max_power=300

def aom_scan(freq_range=[],average=50,target_power=0.1/1000,setpower_tolerance=1e-6,wavelength=780,cf=False,cal_data=[],initset_power=150,k1=1e5,pm_setrange=3):
    if ((freq_range==[]) and (cal_data==[])):
        print ("Specify freq_scan by either freq_range or calibrated table cal_data" )
        return
    init_power=200
    init_freq=180
    Power_meter_address = '/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Optical_Power_Meter_OPM-QO04-if00'
    pm = PowerMeterComm(Power_meter_address)
    pm.set_range(pm_setrange)
    initset_power=initset_power
    powers = []
    powers_adj=[]
    setpower=[]
    setpower_track=[]
    powers_track=[]
    std_powers=[]
    if cal_data!=[]:
        freq_range=cal_data[:,0]
        amp=cal_data[:,1]
    for i in range(len(freq_range)):
        
        dds.set_freq(freq_range[i])#set freq point
        if cal_data!=[]:
            dds.set_power(amp[i])
            ps=amp[i]
        else:
            dds.set_power(init_power)
            ps=initset_power
        
        #wind.set_freq(freq_range[i])
        value = []
        if i<10:
            time.sleep(5)
        else:
            time.sleep(1)
        for m in range(50):
            power = pm.get_power(wavelength)
            value.append(power)
            time.sleep(1e-2) # delay between asking for next value
        p=np.mean(value)
        print('freq:',freq_range[i])
        print('NO ADJUSTMENT OPTICAL POWER',p)
        powers.append(np.mean(value)) #average value to get more reliable number
        std_powers.append(np.std(value))
        num_turn=0
        if cf==True:
            
            while( (p<(target_power-setpower_tolerance)) or (p>(target_power+setpower_tolerance)) ):
                deltap=(target_power-p)
                e=deltap
                deltaps=k1*e
                ps=ps+deltaps
                print('freq:',freq_range[i])
                print('delp:',str(deltap))
                print('step:',str(deltaps))
                
                print('powerset:',ps)
                dds.set_power(int(ps))
                setpower_track.append(ps)
                value=[]
                time.sleep(0.1)
                for m in range(average):
                    power = pm.get_power(wavelength)
                    value.append(power)
                    time.sleep(5e-2) # delay between asking for next value
                p=np.mean(value)
                powers_track.append(p)
                print(p)
                num_turn=num_turn+1
                if ((ps>max_power) or (ps<0) or (num_turn>300)):
                    break
            setpower.append(int(ps))
            value=[]
            for m in range(average):
                power = pm.get_power(wavelength)
                value.append(power)
                time.sleep(5e-2) # delay between asking for next value
            powers_adj.append(np.mean(value))

    dds.set_power(init_power)
    dds.set_freq(init_freq)
    if cf==True:
        calibrated_file=np.column_stack((freq_range,setpower,np.array(powers_adj)*1000.0,np.array(powers)*1000))
        return (calibrated_file,setpower_track,powers_track) # Coonvert to mW
    else:
        return (freq_range,powers,std_powers)
def singlefreq(freq,prf,average=50):
    pm_setrange=3
    f=freq
    #time.sleep(10)
    dds.set_freq(f)
    dds.set_power(prf)
    Power_meter_address = '/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Optical_Power_Meter_OPM-QO04-if00'
    pm = PowerMeterComm(Power_meter_address)
    pm.set_range(pm_setrange)
    value=[]
    time.sleep(10)
    for m in range(average):
                    power = pm.get_power(wavelength)
                    value.append(power)
                    time.sleep(5e-2) # delay between asking for next value
    p=np.mean(value)
    return(f,value,p)
if __name__=="__main__":

    #to scan aom freq and measure optical power without adjustment
    #power_scan(freq_range)
    # set starting power make it low to ensure have enough adjustment when far from AOM resonance
    
   # refix=aom_scan(freq_range,cf=False,pm_setrange=4)
    #updat=np.genfromtxt('u_2.txt')
    #re=aom_scan(freq_range,cf=True,pm_setrange=3,cal_data=updat,target_power=0.05/1000,k1=5e5)
#  
    #plt.plot(freq_range,powers,'-o')#plot data to make sure it makes sense
    #plt.plot(freq_range,fixpowers,'-o',color='red')#plot data to make sure it makes sense
    
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Power (mW)')
    plt.show()
    fig2=plt.figure()
    #plt.plot(freq_range,setpower,'-o',color='black')#plot data to make sure it makes sense1
    plt.show()
    #data = np.column_stack((freq_range,setpower,powers,powers_adj))
    #np.savetxt('power_calibrationup.txt',data)
    updat=np.genfromtxt('u_4.txt')
    #psinglefreq=[]
    #(re,dump1,dump2)=aom_scan(freq_range,cf=True,pm_setrange=3,cal_data=updat,target_power=0.045/1000,k1=5e5,setpower_tolerance=1e-6)
    #(f,p,mp)=singlefreq(178,70,average=200)
    #print(mp)
    #plt.plot(p)
    downdat=np.genfromtxt('d_2.txt')
    
    for i in range(1):
        #(f,powers,std)=aom_scan(freq_range,cf=False,pm_setrange=3,cal_data=downdat,target_power=0.07/1000,k1=5e5)
        #f=re[:,0]
        #powers_adj = re[:,3]#run scan should take about a minute with 10 averages
        time.sleep(1)
        (re,dump1,dump2)=aom_scan(freq_range,cf=True,pm_setrange=3,cal_data=downdat,target_power=0.08/1000,k1=5e5)
        #plt.errorbar(f,powers,yerr=std,fmt='-o')
    
        
    
    
        


