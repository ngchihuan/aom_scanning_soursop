# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 14:20:56 2016

@author: NgChiHuan

FREQ SCANNING BY 2 AOM

VERSION: 1.3

AUTHOR: CHI HUAN

USAGE:
        Scan optical beam frequency up and down with 2 Double Pass AOM

        Able to choose optical detection method: apd or power meter

        Scan with fix rf power to AOM or rf power retrieved from the
        pre-calibrated files

COMMANDS:   scan_updown(fs,fst,device,tableup,tabledown,directo,step=2,fixrfp=False,detector='pm'):

            fs,fst: starting and final scanning freq
            device: DDS address
            tableup/down: calibrated file for aom up/down
            directo: path to store timestamp file
            step: scanning step
            fixfrp=False: if True, extra 1 more round of scanning with fix rf
                            power to aom
            detector=optical detection method

OUTPUT:     (freq,np.array(powers)*1e6,np.array(powers_adj)*1e6)
            freq: scanning freq
            powers: optical power without adjustment
            power_adj: ~ with adjustment




"""

from CQTdevices import DDSComm, PowerMeterComm, WindFreakUsb2,AnalogComm
#import matplotlib.pylab as plt
import numpy as np
import time
import timestampcontrol as tsc
from Counter import Countercomm
import matplotlib.pyplot as plt
def setdds(table,channel,device,freq=180,fixamp=50):
    '''
    Retrieve rf power set to DDS for a frequency from the calibrated table(an array)
    '''
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

def scan_logic(freq,tableup,tabledown,device,fixamp=50):
    '''
    determine the rf freq needed to set to two double pass aom (one up and one down)
    and send command to dds with these freq and power=fixamp
    if freq optical=2=> aom up=176, down=175
    '''

    datup=np.genfromtxt(tableup)
    datdown=np.genfromtxt(tabledown)

    f_up=datup[:,0]
    amp_up=datup[:,1]
    l_up=len(f_up)

    f_down=datdown[:,0]
    amp_down=datdown[:,1]
    l_down=len(f_down)

    step=2
    #the maximum and minimum freq can be scanned
    maxf=2*(f_up[l_up-1]-f_down[0])
    minf=2*(f_up[0]-f_down[l_down-1])
    '''
    ifreq=175#init f
    if (freq>0):
        if ((freq%4)==0):
            f_down=ifreq-freq/4
            f_up=ifreq+freq/4

        else:
           f_down=ifreq

           f_up=freq/2+ifreq

    elif freq<0:
         if ((freq%4)==0):
            f_down=ifreq-freq/4
            f_up=ifreq+freq/4

         else:
           f_up=ifreq
           f_down=-freq/2+ifreq

    else:
           f_up=ifreq
           f_down=ifreq
    '''
    ifreq=150#init f
    if (freq>0):
            f_down=ifreq
            f_up=ifreq+freq/2
    elif freq<0:
            f_up=ifreq
            f_down=ifreq-freq/2
    else:
            f_up=ifreq
            f_down=ifreq
    #command dds to 2 aom
    ampd=setdds(datdown,0,device,freq=f_down,fixamp=fixamp)
    ampu=setdds(datup,1,device,freq=f_up,fixamp=fixamp)
    print('f fup fdown ampup ampdown')
    print(freq,f_up, f_down,ampu,ampd)
    return (ampd,ampu,f_up,f_down)
def scan_updown_setup(fs,fst,device,tableup,tabledown,directo,step=2,fixrfp=False,detector='pm',cf=False,target_power=0.2,setpower_tolerance=0.001,k1=100):
    '''
    scan laser beam freq with 2 aoms
    optical power measurement= powermeter(pm) or apd(using timestamp)
    '''
    if detector=='pm':
        Power_meter_address = '/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Optical_Power_Meter_OPM-QO04-if00'
        pm = PowerMeterComm(Power_meter_address)
        pm.set_range(2)
    if detector=='analog_pm':
        analogpm_add='/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Analog_Mini_IO_Unit_MIO-QO13-if00'
        apm=AnalogComm(analogpm_add)
    table=[]
    freq=np.arange(fs,fst,step)
    average=200
    wavelength=780
    powers_adj=[]
    powers_adj_2=[]
    powers=[]
    fup=[]
    fd=[]
    pup=[]
    pd_f=[]
    setpower_up=[]
    setpower_down=[]
    for i in range(len(freq)):
        (pd,pupp,fupp,fdd)=scan_logic(freq[i],tableup,tabledown,device,fixamp=0)#adjust power for compensation
        #wind.set_freq(freq_range[i])

        fup.append(fupp)
        fd.append(fdd)
        pup.append(pupp)
        pd_f.append(pd)
        value = []
        time.sleep(1)
        p=0
        if detector=='pm':
            for m in range(50):
                power = pm.get_power(wavelength)
                value.append(power)
                time.sleep(5e-2) # delay between asking for next value
            p=np.mean(value)
            powers_adj.append(p)
            print('Power measured is: ',p)
        elif detector=="apd":
                name=tsc.filename(str(freq[i]),directo)
                tsc.start(name=name)
                time.sleep(3)
                tsc.stop()
                time.sleep(1)
        elif detector=='analog_pm':
                for m in range(average):
                    power = apm.get_voltage(0)
                    value.append(float(power))
                    time.sleep(1e-2) # delay between asking for next value

                p=np.mean(value)
                powers.append(p)
        if fixrfp==True:
            scan_logic(freq[i],tableup,tabledown,device,fixamp=180)
            value = []
            time.sleep(5)
            p=0
            if detector=='pm':
                for m in range(average):
                    power = pm.get_power(wavelength)
                    value.append(power)
                    time.sleep(1e-2) # delay between asking for next value
                p=np.mean(value)
                powers.append(p)
            elif detector=='analog_pm':
                for m in range(average):
                    power = apm.get_voltage(0)
                    value.append(float(power))
                    time.sleep(1e-2) # delay between asking for next value

                p=np.mean(value)
                powers.append(p)
        ####################################################################
        #Correcting for uniformity stage
        #####################################################################
        max_power=200
        num_turn=0
        if cf==True:
            print('Starting Correcting...')
            setpower_track=[]
            powers_track=[]
            num_turn=0
            dds1 = DDSComm(DDS_address,1)
            dds0 = DDSComm(DDS_address,0)
            if (freq[i]<=0):
                dds=dds1
                dds0.set_power(pd)
                dds0.set_freq(fdd)
                ps=pupp
                print('Correcting AOM UP,starting Prf: ',ps)
            else:
                dds=dds0
                dds1.set_power(pupp)
                dds1.set_freq(fupp)
                ps=pd
                print('Correcting AOM DOWN,starting Prf: ',ps)
            while( (p<(target_power-setpower_tolerance)) or (p>(target_power+setpower_tolerance)) ):
                deltap=(target_power-p)
                e=deltap
                deltaps=k1*e
                ps=ps+deltaps

                print('freq:',freq[i])
                print('delp:',str(deltap))
                print('step:',str(deltaps))

                print('powerset:',ps)

                dds.set_power(int(ps))


                setpower_track.append(ps)
                value=[]
                time.sleep(1e-1)
                if detector=='pm':
                    for m in range(average):
                        power = pm.get_power(wavelength)
                        value.append(power)
                        time.sleep(1e-2) # delay between asking for next value
                    p=np.mean(value)
                    powers.append(p)
                elif detector=='analog_pm':
                    for m in range(average):
                        power = apm.get_voltage(0)
                        value.append(float(power))
                        time.sleep(1e-2) # delay between asking for next value

                    p=np.mean(value)
                    powers.append(p)
                print('Power measured: ',p)
                print('Set rf power: ',ps)
                num_turn=num_turn+1
                if ((ps>max_power) or (ps<0) or (num_turn>300)):
                    break
                time.sleep(1e-2)
            time.sleep(1)
            if (freq[i]<=0):
                setpower_up.append(int(ps))
                setpower_down.append(int(pd))
            else:
                setpower_up.append(int(pupp))
                setpower_down.append(int(ps))
            value=[]
            if detector=='pm':
                    for m in range(average):
                        power = pm.get_power(wavelength)
                        value.append(power)
                        time.sleep(1e-2) # delay between asking for next value
                    p=np.mean(value)
                    powers.append(p)
            elif detector=='analog_pm':
                    for m in range(average):
                        power = apm.get_voltage(0)
                        value.append(float(power))
                        time.sleep(1e-2) # delay between asking for next value

                    p=np.mean(value)
                    powers.append(p)

            print('after correcting, P is: ',np.mean(value))
            print('*************')
            powers_adj_2.append(np.mean(value))

    table=np.column_stack((freq,fup,fd,pup,pd_f,setpower_up,setpower_down))

    print('Checking result...')
    print('Before/without correcting')
   # plt.plot(freq,powers_adj,'-o')
    print('Scanning new calibrated table')
    (fc,pc)=scan_table(table,DDS_address,detector='analog_pm')
    print('After correcting')
    print(fc,pc)
    plt.plot(fc,pc,'-o',color='red')
    return (freq,np.array(powers)*1e6,np.array(powers_adj)*1e6,np.array(powers_adj_2)*1e6,table)

def scan_table(table,DDS_address,freq=None,detector='pm',directo='probescan/settest', duration=5,umc_average=10):
    '''
    To scan probe freq by 2 aom with pre-defined calibrated rf power.

    The calibrated values OF 2 AOMs stored in the table obtained from the polishing
    process

    Scan the whole table if freq is not specified


    '''
    average=200

    wavelength=780
    if detector=='pm':
        Power_meter_address = '/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Optical_Power_Meter_OPM-QO04-if00'
        pm = PowerMeterComm(Power_meter_address)
        pm.set_range(2)
    if detector=='analog_pm':
        analogpm_add='/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Analog_Mini_IO_Unit_MIO-QO13-if00'
        apm=AnalogComm(analogpm_add)
    if detector=='usbmini-counter':
        counter_add='/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_USB_Counter_Ucnt-QO10-if00'
        counter=Countercomm(counter_add)
        counter.set_gate_time(30)
    f=table[:,0]
    fup=table[:,1]
    fdown=table[:,2]
    pup=table[:,5]
    pd=table[:,6]
    if freq!=None:
        print('Freq: ',freq)
        
        i=np.where(table[:,0]==freq)[0][0]
        fu=fup[i]
        fd=fdown[i]
        print('fup fd',fu,fd)
        ampup=pup[i]
        ampd=pd[i]

        dds = DDSComm(DDS_address,0)
        dds.set_freq(fd)
        dds.set_power(ampd)

        dds1= DDSComm(DDS_address,1)
        dds1.set_freq(fu)
        dds1.set_power(ampup)
        time.sleep(2)
        if detector=='pm':
                value=[]
                for m in range(average):
                    power = pm.get_power(wavelength)
                    value.append(power)
                    time.sleep(1e-1) # delay between asking for next value
                p=np.mean(value)

        elif detector=='analog_pm':
                for m in range(average):
                    power = apm.get_voltage(0)
                    value.append(float(power))
                    time.sleep(1e-2) # delay between asking for next value

                p=np.mean(value)
                powers.append(p)
                print('Power: ',p)
        elif detector=="apd":
                name=tsc.filename(str(freq),directo)
                tsc.start(name=name)
                time.sleep(duration)
                tsc.stop()
                time.sleep(0.5)
                return name
        elif detector=="usbmini-counter":
                value=[]

                for m in range(umc_average):
                    value.append((counter.get_counts(0)))
                p=np.mean(value)
                return(freq,value)

    if freq==None:
        #Scan the whole table
        print('scan the whole table')
        powers=[]
        #for i in range(len(f)):
        fscan=[]
        for i in range(len(f)):
            fscan.append(f[i])
            fu=fup[i]
            fd=fdown[i]
            ampup=pup[i]
            ampd=pd[i]
            print(fu,fd)
            dds = DDSComm(DDS_address,0)
            dds.set_freq(fd)
            dds.set_power(ampd)

            dds1= DDSComm(DDS_address,1)
            dds1.set_freq(fu)
            dds1.set_power(ampup)
            time.sleep(1)
            value=[]
            std=[]
            if detector=='pm':

                for m in range(average):
                    power = pm.get_power(wavelength)
                    value.append(power)
                    time.sleep(1e-1) # delay between asking for next value
                p=np.mean(value)
                std=np.std(value)
                print('Freq ',f[i])
                print(p,std)
                powers.append(p)

            elif detector=="apd":
                directo='probescan/set2'
                name=tsc.filename(str(f[i]),directo)
                tsc.start(name=name)
                time.sleep(0.5)
                tsc.stop()
                time.sleep(2)
            elif detector=='analog_pm':
                for m in range(average):
                    power = apm.get_voltage(0)
                    value.append(float(power))
                    time.sleep(1e-2) # delay between asking for next value

                p=np.mean(value)
                powers.append(p)
                print('P is: ',p)
                print('Freq:',f[i])
        return (fscan,powers)
def scanloop(f,table,numl=100):
    DDS_address = '/dev/ioboards/dds_QO0037'
    pa=[]
    for i in range(numl):

        p=scan_table(table,DDS_address,freq=f,detector='pm')
        pa.append(p)
        print(p)
    return pa
if __name__=='__main__':
    DDS_address = '/dev/ioboards/dds_QO0037'
    tableup=('u_4.txt')
    tabledown=('d_3.txt')
    dtup=np.genfromtxt(tableup)
    dtd=np.genfromtxt(tabledown)
    directo='probescan/set1'
    #scan_logic(0,tableup,tabledown,DDS_address,fixamp=0)#adjust power for compensation
    '''    
    (freq,powers,powers_adj,powers_adj_2,table)=scan_updown_setup(-100,100,DDS_address,tableup,tabledown,directo,step=2,detector='analog_pm',cf=True,target_power=0.1)
    np.savetxt('calibrated_table_3.txt',table)
    '''
    #plt.plot(freq,powers,'-o')
    
    table = np.genfromtxt('calibrated_table_3.txt')
    #(fc,pc)=scan_table(table,DDS_address,detector='analog_pm')
    plt.plot(fc,pc)

    #plt.plot(freq,powers_adj,'-o',color='blue')0
    #plt.plot(freq,powers_adj_2,'-o',color='red')
    #freq=table[:,0]0
    #plt.show()
    #table=np.genfromtxt('table_4_s40.txt')
    #pa=scanloop(-100,table)
    #print(np.std(pa))
   # plt.plot(pa)

   #------SCAN THE WHOLE TABLE------------#
    #table=np.genfromtxt('calibrated_table.txt')
    #(f,powers)=scan_table(table,DDS_address,freq=None,detector='analog_pm')
