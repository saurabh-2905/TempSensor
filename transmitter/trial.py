import sys
import utime
from lib.varlogger import VarLogger as vl
from machine import Timer



##### try one wire sensor ########
# import time
# from machine import Pin
# from ds18x20 import DS18X20
# from onewire import OneWire


# # DS18B20 data line connected to pin P10
# ow = OneWire(Pin('P10', Pin.OPEN_DRAIN))
# temp = DS18X20(ow)
# print("Powermode = ", temp.powermode(Pin('P11')))
# roms = temp.scan()

# temp.resolution(roms[0], 9)
# print("Resolution", temp.resolution(roms[0]))

# temp.convert_temp()
# while True:
#     time.sleep(1)
#     for rom in roms:
#         print(temp.read_temp(rom), end=" ")
#     print()
#     temp.convert_temp()

import time
from machine import Pin
from ds18x20_single import DS18X20Single
from onewire import OneWire

# DS18B20 data line connected to pin P10
ow = OneWire(Pin('P10'))
temp = DS18X20Single(ow)
#print("Powermode = ", temp.powermode(Pin('P11')))

temp.convert_temp()
while True:
    time.sleep(1)
    print(temp.read_temp())
    temp.convert_temp()

# ###### catch traceback #####
# def trial():
#     a = [1,2,3]

#     try:
#         print(a)
#         print(a[3])
#     except Exception as e:
#         vl.traceback(e)
        
# #trial()

# ##### test timer interrupt ######

# class Clock():
#     def start(self, time):
#         '''
#         time in ms
#         '''
#         self.alarm = Timer.Alarm(handler=self.cb, ms=time, periodic=True)

#     def cb(self, alarm):
#         #lock.acquire()
#         #control.clock_set()
#         #lock.release()
#         print('clock done')

#     def stop(self):
#         self.alarm.cancel()
#         print('clock stopped')