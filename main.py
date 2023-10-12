# TODO Add machine.reset() on error with hardware, set timer for restart if connection to TTN impossible 


import pycom
import time
from machine import Pin, I2C, SD
import os
from network import WLAN
import usocket as socket
import uselect
import _thread
import uerrno
import json

# Imports of classes that represent the connected sensors and devices
from dht import DTH
from adxl345 import ADXL345
from itg3200 import ITG3200
from buzzer import Buzzer
# Import of a file containing functions for connecting to TTN.
import LoRaConnection

# Import Pysense libraries
from pycoproc_2 import Pycoproc

from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

from lib.varlogger import VarLogger as logger



# This function resides in the LoRaConnection.py file. It is used to create the connection to The Things Network and block further execution until a connection has been established
LoRaConnection.connectToTTN()


# print ("Welcome")
# currentSsid = '73569a'
# currentPassword = '285254244'

# wlan = WLAN(mode=WLAN.STA)
# wlan.connect(ssid=currentSsid, auth=(WLAN.WPA2, currentPassword))
# while not wlan.isconnected():
#     time.sleep(1)
#     print("Wifi ... Connecting to " + currentSsid)

# print ("Wifi is Connected")

# init pyproc for reading data
py = Pycoproc()

# Turn off the PyCom "Heartbeat" - the constant blinking of the indicator LED
pycom.heartbeat(False)

# Set indicator LED to red in order to signify that a successful connection has been established and that the sensor readout is now starting
pycom.rgbled(0x8B0000) # red
time.sleep(5)

# # Below is the initialisation of all hardware components that are connected to the LoPy4
# # The th variable contains an instance of the DTH class from a driver library which reads out the binary data from the sensor and converts it to temperature (C) and humidity (%).
# # The data pin of the DHT11 is connected to pin 23
# th = DTH(Pin('P23', mode=Pin.OPEN_DRAIN),0)
si = SI7006A20(py)

# # The adx and itg variables hold instances of classes that represent the ADXL345 accelerometer and ITG3200 gyroscope respectively.
# # We pass the I2C bus to the classes in order for them to know which pins the bus is connected to.
# adx = ADXL345(i2c)
# itg = ITG3200(i2c)
li = LIS2HH12(py)



# The buzzer variable holds an instance of the Buzzer class that represents the piezo-speaker connected to pin 20 of the LoPy4.
# buzzer = Buzzer(buzzerPin='P20')

# url = '192.168.0.11'

# The tenMinutes and thirtyMinutes variables hold values of ten and thirty minutes in seconds, respectively.
tenMinutes = 1 * 60
thirtyMinutes = 3 * tenMinutes

# The variables below are used to store the last second from initialisation of the system in which data was transmitted to TTN or at which the temperature and humidity were captured and written to currentIntervalTemperatureHumidity.
lastTransmitTime = 0
lastTempHumCaptureTime = 0

# This variable holds the current temperature and humidity until transmission. Temperature and humidity are written to this array every 10 minutes, transmission is every 30 minutes due to the limitations of TTN.
currentIntervalTemperature = []
currentIntervalHumidity = []

prevXAcceleration = None
prevYAcceleration = None
prevZAcceleration = None

# This is the main part of the programme which runs in an infinite loop until the device is stopped or an error occurs. Indicator set to green to show arrival at main loop
pycom.rgbled(0x001000) # green
while True:
    # The current time variable gets updated constantly to hold the current time for this loop
    currentTime = time.time()

    # The acceleration info is requested from the sensor at every loop
    acceleration = li.acceleration()
    print("Acceleration: " + str(acceleration))
    xAcceleration = acceleration[0]
    yAcceleration = acceleration[1]
    zAcceleration = acceleration[0]

    # gyroResult = itg.result
    # xGyro = gyroResult[0]
    # yGyro = gyroResult[1]
    # zGyro = gyroResult[2]                                     

    if (prevXAcceleration and prevYAcceleration and prevZAcceleration):
        xDiff = abs(xAcceleration - prevXAcceleration)
        yDiff = abs(yAcceleration - prevYAcceleration)
        zDiff = abs(zAcceleration - prevZAcceleration)

        xCondition = xDiff > 1.4
        yCondition = yDiff > 0.51
        zCondition = zDiff > 0.48

        shouldTriggerAlarm = (xCondition and yCondition) or (xCondition and zCondition) or (yCondition and zCondition)

        if (shouldTriggerAlarm):
            print('Alarm triggered')
            # buzzer.playAlarm()
            # time.sleep(1)
            # buzzer.stopAlarm()
            LoRaConnection.sendSocketData(bytearray([1]))

    prevXAcceleration = xAcceleration
    prevYAcceleration = yAcceleration
    prevZAcceleration = zAcceleration
        
    # If it has been at least 10 minutes since the last capture of temperature and humidity, we get the data from the DHT11 and store it in lists
    if (currentTime - lastTempHumCaptureTime >= tenMinutes or lastTempHumCaptureTime == 0):
        lastTempHumCaptureTime = time.time()
        print('Trying to capture temperature')
        temperature = round(si.temperature())
        humidity = round(si.humidity())

        currentIntervalTemperature.append(temperature)
        currentIntervalHumidity.append(humidity)

    # If it has been at least thirty minutes since the last transmission, we calculate the average of the captured temperature and humidity data and send it to the TTN using LoRaWAN sockets.
    if(currentTime - lastTransmitTime >= thirtyMinutes):
        lastTransmitTime = time.time()
        print('Transmitting')
        print(currentIntervalTemperature)
        if (len(currentIntervalTemperature) > 0 and len(currentIntervalHumidity) > 0):
            averageTemperature = int(sum(currentIntervalTemperature)/len(currentIntervalTemperature))
            averageHumidity = int(sum(currentIntervalHumidity)/len(currentIntervalHumidity))
            print('Clearing lists')
            currentIntervalTemperature.clear()
            currentIntervalHumidity.clear()
            sensorData = {
                "time": time.time(),
                "temperature": averageTemperature,
                "humidity": averageHumidity,
                "xAcceleration": xAcceleration,
                "yAcceleration": yAcceleration,
                "zAcceleration": zAcceleration,
            }
            dataForSocket = bytes([averageTemperature, averageHumidity])
            print(dataForSocket)
            LoRaConnection.sendSocketData(dataForSocket)


    time.sleep_ms(100)



# s = socket.socket()
# s.connect(socket.getaddrinfo(url, 9090)[0][-1])
# dataForSocket = json.dumps(sensorData)
# s.send(dataForSocket)
# # Wait for the response and receive it in a variable
# response = s.recv(len(dataForSocket))
# print("RESPONSE: ", response)
# s.close()