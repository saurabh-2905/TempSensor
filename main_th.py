### Import Pysense libraries
from pycoproc_2 import Pycoproc
import pycom
import _thread
from network import LoRa
import socket
import time

from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
### Import of a file containing functions for connecting to TTN.
import LoRaConnection

from varlogger import VarLogger as logger

### initialize logger
### initialize it outside the scope of any function to allow access to all the code
logt = logger()

### put all the functionality in different functions to be able to run in multiple threads, use a class with methods as '@classmethod' so that we can pass class itslef as an argument and dont need to make an instance to be able to use class variables
def main():
    lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
    ### init pyproc for reading data
    py = Pycoproc()

    ### Turn off the PyCom "Heartbeat" - the constant blinking of the indicator LED
    pycom.heartbeat(False)

    ### Set indicator LED to blue in order to signify that a successful connection has been established and that the sensor readout is now starting
    pycom.rgbled(0x00008B) # blue
    time.sleep(5)

    ### Below is the initialisation of all hardware components that are connected to the LoPy4
    si = SI7006A20(py)

    ### The adx and itg variables hold instances of classes that represent the ADXL345 accelerometer and ITG3200 gyroscope respectively.
    li = LIS2HH12(py)

    ### The tenMinutes and thirtyMinutes variables hold values of ten and thirty minutes in seconds, respectively.
    tenMinutes = 1 * 60
    thirtyMinutes = 3 * tenMinutes

    ### The variables below are used to store the last second from initialisation of the system in which data was transmitted to TTN or at which the temperature and humidity were captured and written to currentIntervalTemperatureHumidity.
    lastTransmitTime = 0
    lastTempHumCaptureTime = 0

    ### This variable holds the current temperature and humidity until transmission. Temperature and humidity are written to this array every 10 minutes, transmission is every 30 minutes due to the limitations of TTN.
    currentIntervalTemperature = []
    currentIntervalHumidity = []

    prevXAcceleration = None
    prevYAcceleration = None
    prevZAcceleration = None

    ### This is the main part of the programme which runs in an infinite loop until the device is stopped or an error occurs. Indicator set to green to show arrival at main loop
    pycom.rgbled(0x008B00) # green
    time.sleep(5)

    ### sense the data
    acceleration = sense(li)

    ### send the data via lora communication
    # acquire lock
    # write data to shared resource
    # set the flag of communication 
    # release the lock

    ### Turn on the PyCom "Heartbeat" - the constant blinking of the indicator LED
    pycom.heartbeat(True)



def sense(li):
    # The acceleration info is requested from the sensor at every loop
    acceleration = li.acceleration()
    print("Acceleration: " + str(acceleration))
    xAcceleration = acceleration[0]
    yAcceleration = acceleration[1]
    zAcceleration = acceleration[0]

    return acceleration
    

def process():
    pass

def loracom():
    
    # check for the communication flag
    # acquire the lock
    # get the data from shared resource
    # release the lock

    ### create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    ### make the socket blocking
    ###(waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(False)

    ### send some data
    s.send(data)

    ### make the socket non-blocking
    ### (because if there's no data received it will block forever...)
    s.close()


class threadcom:
    @classmethod
    def timerflag(cls):
        pass

    @classmethod
    def sharedres(cls):
        pass


    main_thread = _thread.start_new_thread(main, ())