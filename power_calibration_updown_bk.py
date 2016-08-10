# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:41:43 2015

@author: Nick Lewty
"""

from CQTdevices import DDSComm, PowerMeterComm, WindFreakUsb2
import matplotlib.pylab as plt
import numpy as np
import time



# location of devices
Power_meter_address = '/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Optical_Power_Meter_OPM-QO04-if00'

DDS_address = '/dev/ioboards/dds_QO0037'
DDS_channel = 1

#Connect to devices and create objects
pm = PowerMeterComm(Power_meter_address)

ddsup = DDSComm(DDS_address,1)
ddsd = DDSComm(DDS_address,0)
#wind = WindFreakUsb2('/dev/serial/by-id/usb-Windfreak_Synth_Windfreak_CDC_Serial_014571-if00')


#Frequency range to scan in MHz
start = -70
stop = 70
step = 2

freq_range = np.arange(start,stop,step)

init_power_up=200
init_freq_up=200

init_power_down=150
init_freq_down=180

initset_power=100
setpower_tolerance=0.01/1000
target_power=0.1/1000
max_power=180
def power_scan(freq_range,average=10,wavelength=780):
	powers = []
	powers_adj=[]
	for i in range(len(freq_range)):
		if (freq_range[i]>0):
			ddsup.set_freq(220)
			dds=ddsd
			freq=220-freq_range[i]
		else:
			ddsd.set_freq(220)
			dds=ddsup
			freq=220+freq_range[i]
		dds.set_freq(freq)#set freq point
		#wind.set_freq(freq_range[i])
		value = []
		time.sleep(0.1)
		for i in range(average):
			power = pm.get_power(wavelength)
			value.append(power)
			time.sleep(5e-3) # delay between asking for next value
		p=np.mean(value)
		print('freq:',freq_range[i])
		print(p)
		powers.append(np.mean(value)) #average value to get more reliable number
		t=1
		ps=initset_power
		num_turn=0
		while( (p<(target_power-setpower_tolerance)) or (p>(target_power+setpower_tolerance)) ):
			sign=0
			if p>target_power:
				sign=-1
			else:
				sign=1
			t=abs(p-target_power)*1e5
			print('freq:',freq_range[i])
			print('delp:',str(p-target_power))
			print('tstep:',t)
			ps=ps+sign*t
			print('powerset:',ps)
			dds.set_power(int(ps))
			value=[]
			for i in range(average):
				power = pm.get_power(wavelength)
				value.append(power)
				time.sleep(5e-3) # delay between asking for next value
			p=np.mean(value)
			print(p)
			num_turn=num_turn+1
			if ((ps>max_power) or (ps<0) or (num_turn>50)):
				break
		value=[]
		for i in range(average):
			power = pm.get_power(wavelength)
			value.append(power)
			time.sleep(5e-3) # delay between asking for next value
		powers_adj.append(np.mean(value))
		dds.set_power(initset_power)
	return (np.array(powers_adj)*1000.0,np.array(powers)*1000) # Coonvert to mW
dds.set_freq(init_freq)
dds.set_power(init_power)


#Calibration procedure

pm.set_range(3) # set suitable range for optical power being measured

# set starting power make it low to ensure have enough adjustment when far from AOM resonance

powers = power_scan(freq_range)[1]#run scan should take about a minute with 10 averages
powers_adj = power_scan(freq_range)[0]
plt.plot(freq_range,powers,'-o')#plot data to make sure it makes sense
plt.plot(freq_range,powers_adj,'-o',color='red')#plot data to make sure it makes sense
plt.xlabel('Frequency (MHz)')
plt.ylabel('Power (mW)')
plt.show()
data = np.column_stack((freq_range,powers))
np.savetxt('power_calibration.txt',data)
	
	
		


