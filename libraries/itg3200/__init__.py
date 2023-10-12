# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# ITG-3200
# This code is designed to work with the ITG-3200_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Gyro?sku=ITG-3200_I2CS#tabs-0-product_tabset-2
# Modified ITG3200 code to work without smbus on PyCom devices in Micropython
from machine import Pin,I2C
import math
import time

device = const(0x68)
regAddress = const(0x1D)
TO_READ = 6
buff = bytearray(6)

class ITG3200:
    def __init__(self,i2c,addr=device):
        self.addr = addr
        self.i2c = i2c
        # ITG3200 address, 0x68(104)
        # Select Power management register 0x3E(62)
        #		0x01(01)	Power up, PLL with X-Gyro reference
        self.i2c.writeto_mem(0x68, 0x3E, 0x01)
        # ITG3200 address, 0x68(104)
        # Select DLPF register, 0x16(22)
        #		0x18(24)	Gyro FSR of +/- 2000 dps
        self.i2c.writeto_mem(0x68, 0x16, 0x18)
        time.sleep(0.5)

    @property
    def result(self):
        buff = self.i2c.readfrom_mem(self.addr,0x1D,TO_READ)
        xGyro = buff[0] * 256 + buff[1]
        if xGyro > 32767 :
	        xGyro -= 65536
        yGyro = buff[2] * 256 + buff[3]
        if yGyro > 32767 :
        	yGyro -= 65536
        zGyro = buff[4] * 256 + buff[5]
        if zGyro > 32767 :
        	zGyro -= 65536
        return [xGyro, yGyro, zGyro]

    @property
    def xGyro(self):
        buff = self.i2c.readfrom_mem(self.addr,0x1D,TO_READ)
        print(buff[0])
        print(buff[1])
        xGyro = buff[0] * 256 + buff[1]
        print(xGyro)
        if xGyro > 32767 :
	        xGyro -= 65536
        print(xGyro)
        return xGyro
   
    @property
    def yGyro(self):
        buff = self.i2c.readfrom_mem(self.addr,0x1D,TO_READ)
        yGyro = buff[2] * 256 + buff[3]
        if yGyro > 32767 :
        	yGyro -= 65536
     
    @property   
    def zGyro(self): 
        buff = self.i2c.readfrom_mem(self.addr,0x1D,TO_READ)
        zGyro = buff[4] * 256 + buff[5]
        if zGyro > 32767 :
        	zGyro -= 65536