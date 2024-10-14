### Import Pysense libraries
from pycoproc_2 import Pycoproc
import pycom
import _thread
from network import LoRa
import socket
import utime
import machine
from machine import Timer
import sys

from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20

from machine import Pin
from ds18x20_single import DS18X20Single
from onewire import OneWire

### Import of a file containing functions for connecting to TTN.
import LoRaConnection

# from lib.varlogger import VarLogger as vl

#############################
#### Single Thread Code #####
#############################

### declare global variables
global g_ack
g_ack = False

### put all the functionality in different functions to be able to run in multiple threads, use a class with methods as '@classmethod' so that we can pass class itslef as an argument and dont need to make an instance to be able to use class variables
def main():
    try:
        #print('thread id1:', _thread_id)

        ### declare global variables
        global g_ack

        #/// update the thread status

        ### init pyproc for reading data
        #py = Pycoproc()
        #//// logging

        #### one wire temp sensor
        ow = OneWire(Pin('P10'))
        temp = DS18X20Single(ow)
        temp.convert_temp()

        lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
        #//// logging

        lora.callback(LoRa.RX_PACKET_EVENT, handler=lora_cb)

        ### create a LoRa socket
        s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        #//// logging

        ### Turn off the PyCom "Heartbeat" - the constant blinking of the indicator LED
        pycom.heartbeat(False)

        ### Set indicator LED to blue in order to signify that a successful connection has been established and that the sensor readout is now starting
        pycom.rgbled(0x00008B) # blue
        utime.sleep_ms(500)

        ### Declare timer
        com_timer = Clock()
        ### start timer
        com_timer.start(5000) ### count for 5 sec
        ### Below is the initialisation of all hardware components that are connected to the LoPy4
        #si = SI7006A20(py)
        #//// logging

        ### The adx and itg variables hold instances of classes that represent the ADXL345 accelerometer and ITG3200 gyroscope respectively.
        #li = LIS2HH12(py)
        #//// logging

        ### This is the main part of the programme which runs in an infinite loop until the device is stopped or an error occurs. Indicator set to green to show arrival at main loop
        pycom.rgbled(0x008B00) # green
        control.init_timer0() ### time in seconds
        i=0
        #//// logging
        while i <2000:
            ### sense the data
            #acceleration = sense(li)
            temperature = sense(temp)
            #//// logging
            ### send the data via lora communication
            
            ### push data to control and signal the communication thread to tx the data
            if temperature != None:
                lock.acquire()
                control.updatedata(temperature)
                #print('temp:', temperature)
                lock.release()
            else: 
                print(temperature)
                with open('temp_log', 'a')as f:
                    f.write("{} {}".format(temperature, utime.ticks_ms() - vl.created_timestamp))

            ### transmit data periodically
            #print('timer status:', control.read_timer0())
            if com_timer.done: ### in ms
                loracom(s, com_timer)

            if g_ack:
                g_ack = False 
                events = lora.events()
                #//// logging

                if events & LoRa.RX_PACKET_EVENT:
                    print('Lora packet received')
                    lock.acquire()
                    ### remove the packet from queue if ack received
                    control.update_rxmsg()
                    lock.release()

            ### testing code
            if i == 1000:
                raise(RuntimeError)

            i+=1
            # print(i, utime.ticks_ms() - vl.created_timestamp)
            #//// logging

        ### Turn on the PyCom "Heartbeat" - the constant blinking of the indicator LED
        pycom.heartbeat(True)
        #//// update the thread status
    except Exception as e:
        #//// save the traces to flash
        print('main thread error:', e)  
        #/// log the traceback message
        #/// update the thread status
        com_timer.stop()
        pycom.heartbeat(True)
        _thread.exit()



def sense(te):
    global start_time

    try: #////
        ### The acceleration info is requested from the sensor at every loop
        #acceleration = li.acceleration()
        temperature = te.read_temp()
        te.convert_temp()
        utime.sleep(1)
    except Exception as e: #////
        #//// save the traces to flash
        #/// log the traceback message
        #/// update the thread status
        pycom.heartbeat(True)

    return temperature
    

def loracom(socket, timer):
    global start_time

    try: #/////
        #print('thread 2:', _thread.get_ident())   
        
        #print('lora:', utime.ticks_diff(utime.ticks_ms(), start_time)) ### use ticks_diff only fordebugging
        lock.acquire()
        data = str(control.readdata()[0])
        lock.release()
        #//// logging
        #print(data)
        
        ### make the socket blocking
        ###(waits for the data to be sent and for the 2 receive windows to expire)
        socket.setblocking(False)

        ### send some data
        socket.send('123456') ### send dummy data to check at receiver side
        lock.acquire()
        ### add the packet to msg_queue to keep track of packet delivery
        control.update_txmsg(data)
        lock.release()
        print('Data sent')
        timer.done = False

        ### make the socket non-blocking
        ### (because if there's no data received it will block forever...)
    except Exception as e: #/////
        #//// save the traces to flash
        #/// log the traceback message
        #//// update the thread status
        pycom.heartbeat(True)

def lora_cb(lora):
    global g_ack
    g_ack = True


class Clock():
    def start(self, time):
        '''
        time in ms
        '''
        self.alarm = Timer.Alarm(handler=self.cb, ms=time, periodic=True)
        self.done = False

    def cb(self, alarm):
        #lock.acquire()
        self.done = True
        #lock.release()
        #print('clock done')

    def stop(self):
        self.alarm.cancel()
        
class control:
    '''
    this class is used to communicate between threads and manage shared resources
    @classmethod: allows to pass the class as the argument, inturn allows to update the attributes of the class without creating the instance of the class
    '''
    sensor_data = []
    tx_flag = False   ### to indidcate transmission if loracom runs in seperate thread
    timer0_done = False ### flag to indicate timer had completed count to trigger other processes
    timer0 = Timer.Chrono()
    msg_queue = []


    @classmethod
    def updatedata(cls, data):
        ### update the sensor data in shared variable
        cls.sensor_data = [data]
        #//// logging
    
    @classmethod
    def readdata(cls):
        ### read the sensor data from shared variable
        return cls.sensor_data
    
    @classmethod
    def init_timer0(cls):
        ### initialize the timer object with duration equal to time
        #cls.timer0.init(Timer.ONE_SHOT, time, cls.sett0)
        #timer0 = Timer.Alarm(cls.sett0, time, periodic=False)  ### time in seconds, as no arguments passed to callback it passes the object itself
        cls.timer0.start()
        print('Timer Initialized')
        #print(cls.timer0.read_ms())  ### check

        #//// logging
    
    @classmethod
    def read_timer0(cls):
        ### get the count of timer0 to check if it has completed counting (milliseconds)
        return cls.timer0.read_ms()
    
    @classmethod
    def reset_timer0(cls):
        ### reset chrono timer
        cls.timer0.reset()

        #//// logging
    
    @classmethod
    def stop_timer0(cls):
        ### stop chrono timer
        cls.timer0.stop()

        #//// logging

    @classmethod
    def update_txmsg(cls, data):
        '''
        data: transmitted packets 
        '''
        cls.msg_queue += [data]
        #print('Tx:', cls.msg_queue)


    @classmethod
    def update_rxmsg(cls):
        '''
        remove the packet if ack received
        '''
        drop = cls.msg_queue.pop(-1)
        print('Rx:',cls. msg_queue)


#####################################################
############### main functionality ##################
#####################################################
try:
    ### initialize it outside the scope of any function to allow access to all the code
    start_time = utime.ticks_ms()
    #### get lock to regulate the access to shared resources
    lock = _thread.allocate_lock()
    #/// update the thread status
    main_thread = _thread.start_new_thread(main, ())
               

except Exception as e:
    #//// save the data
    #/// log the traceback message
    print('Error message:', e)
    pycom.heartbeat(True)