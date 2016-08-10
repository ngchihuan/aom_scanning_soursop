# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 09:44:20 2016

@author: chihuan
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 17:23:06 2015

@author: Nick Lewty

Python software for communicating with Hameg power supply

Simple serial communication based on GPIB commands

For more info on commands see data sheet

http://www.hameg.com/manuals.0.html?&no_cache=1&tx_hmdownloads_pi1[mode]=download&tx_hmdownloads_pi1[uid]=7465 

"""

import serial
import time
class Hameg(object):
    baudrate = 115200
    
    def __init__(self, port):
        self.serial = self._open_port(port)
        
    def _open_port(self, port):
        ser = serial.Serial(port, self.baudrate, timeout=1)
        ser.readline()
        ser.timeout = 1
        return ser
        
    def _serial_write(self, string):
        self.serial.write((string + '\n').encode('utf-8'))
        
    def _serial_read(self):
        msg_string = self.serial.readline()
        # Remove any linefeeds etc
        msg_string = msg_string.rstrip()
        return msg_string
    
    def reset(self):
        self._serial_write('*RST')
        
    def serial_number(self):
        self._serial_write('*IDN?')
        return self._serial_read()
        
    def set_voltage(self,channel,value):
        self._serial_write('INST OUT'+str(channel))
        self._serial_write('VOLT ' + str(value))
        
    def get_voltage(self,channel):
        self._serial_write('INST OUT'+str(channel))
        self._serial_write('MEAS:VOLT?')
        return self._serial_read()
        
    def set_current(self,channel,value):
        self._serial_write('INST OUT'+str(channel))
        self._serial_write('CURR ' + str(value))
        
    def get_current(self,channel):
        self._serial_write('INST OUT'+str(channel))
        self._serial_write('MEAS:CURR?')
        return self._serial_read()
    
    def output_on(self,channel):
        self._serial_write('INST OUT'+str(channel))
        self._serial_write('OUTP ON')
        
    def output_off(self,channel):
        self._serial_write('INST OUT'+str(channel))
        self._serial_write('OUTP OFF')
if __name__=='__main__':
    
    ports="/dev/serial/by-id/usb-HAMEG_HAMEG_HO720_013105245-if00-port0"
    a=Hameg(ports)
    
    #a.set_voltage(1,1)
    v1=3.5
    step=0.5
    a.output_on(1)
    a.set_current(1,4.7)
    time.sleep(600)
    while True:
        a.set_current(1,4.3)        
        time.sleep(600)
        a.set_current(1,3)
   
        a.set_current(1,2)
  
        a.set_current(1,1)        
        time.sleep(0.5)                  
        a.set_current(1,0)        
        time.sleep(600)
        