# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 12:30:47 2016

@author: qitlab
"""

from CQTdevices import DDSComm, PowerMeterComm, WindFreakUsb2
from Counter import Countercomm

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
import imp
import CQTdevices
#imp.reload(CQTdevices.WindFreakUsb2)
imp.reload(CQTdevices)
wf_add='/dev/serial/by-id/usb-Windfreak_Synth_Windfreak_CDC_Serial_014571-if00'
wf=WindFreakUsb2(wf_add)

DDS_address = '/dev/ioboards/dds_QO0037'
DDS_channel_probe=0
dds_probe=DDSComm(DDS_address,DDS_channel_probe)
table=np.genfromtxt('calibrated_table_2.txt')