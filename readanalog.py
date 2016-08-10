# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 15:38:30 2016

@author: qitlab
"""

from CQTdevices import AnalogComm
add='/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Analog_Mini_IO_Unit_MIO-QO02-if00'
r=AnalogComm(add)
re=r.get_voltage(1)
print(re)