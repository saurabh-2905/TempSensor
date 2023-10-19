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
### Import of a file containing functions for connecting to TTN.
import LoRaConnection

from lib.varlogger import VarLogger as vl

#############################
#### Single Thread Code #####
#############################


### put all the functionality in different functions to be able to run in multiple threads, use a class with methods as '@classmethod' so that we can pass class itslef as an argument and dont need to make an instance to be able to use class variables
def main():
    try:
        #///// private variables to log the traces
        _thread_id = _thread.get_ident()
        _fun_name = 'main'
        _cls_name = '0'

        #print('thread id1:', _thread_id)

        #/// update the thread status
        vl.thread_status(_thread_id, 'active')  

        ### init pyproc for reading data
        py = Pycoproc()
        #//// logging
        vl.log(var='py', fun=_fun_name, clas=_cls_name, th=_thread_id) 

        lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
        #//// logging
        vl.log(var='lora', fun=_fun_name, clas=_cls_name, th=_thread_id) 

        ### Turn off the PyCom "Heartbeat" - the constant blinking of the indicator LED
        pycom.heartbeat(False)

        ### Set indicator LED to blue in order to signify that a successful connection has been established and that the sensor readout is now starting
        pycom.rgbled(0x00008B) # blue
        utime.sleep(2)

        ### Below is the initialisation of all hardware components that are connected to the LoPy4
        si = SI7006A20(py)
        #//// logging
        vl.log(var='si', fun=_fun_name, clas=_cls_name, th=_thread_id) 

        ### The adx and itg variables hold instances of classes that represent the ADXL345 accelerometer and ITG3200 gyroscope respectively.
        li = LIS2HH12(py)
        #//// logging
        vl.log(var='li', fun=_fun_name, clas=_cls_name, th=_thread_id) 

        ### This is the main part of the programme which runs in an infinite loop until the device is stopped or an error occurs. Indicator set to green to show arrival at main loop
        pycom.rgbled(0x008B00) # green
        control.init_timer0() ### time in seconds
        i=0
        #//// logging
        vl.log(var='i', fun=_fun_name, clas=_cls_name, th=_thread_id)
        while i <100:
            ### sense the data
            acceleration = sense(li)
            #//// logging
            vl.log(var='acceleration', fun=_fun_name, clas=_cls_name, th=_thread_id)
            utime.sleep(2)
            ### send the data via lora communication
            #lock.acquire()
            ### push data to control and signal the communication thread to tx the data
            control.updatedata(acceleration)

            ### transmit data periodically
            #print('timer status:', control.read_timer0())
            if control.read_timer0() > 5000: ### in ms
                loracom()
                control.reset_timer0() ### time in seconds
            #lock.release()

            # ### testing code
            # if i == 5:
            #     raise(RuntimeError)

            i+=1
            print(i)
            #//// logging
            vl.log(var='i', fun=_fun_name, clas=_cls_name, th=_thread_id)

        ### Turn on the PyCom "Heartbeat" - the constant blinking of the indicator LED
        pycom.heartbeat(True)
        #//// update the thread status
        vl.thread_status(_thread_id, 'dead') 
    except Exception as e:
        #//// save the traces to flash
        vl.save()
        print('main thread error:', e)  
        #/// log the traceback message
        vl.traceback(e)
        #/// update the thread status
        vl.thread_status(_thread_id, 'dead') 
        pycom.heartbeat(True)
        _thread.exit()



def sense(li):
    global start_time#///// private variables to log the traces
    _thread_id = _thread.get_ident()
    _fun_name = 'sense'
    _cls_name = '0'

    #/// update the thread status
    vl.thread_status(_thread_id, 'active') 
    
    try: #////
        ### The acceleration info is requested from the sensor at every loop
        acceleration = li.acceleration()
        #//// logging
        vl.log(var='acceleration', fun=_fun_name, clas=_cls_name, th=_thread_id)
        print("Acceleration: " + str(acceleration), utime.ticks_diff(utime.ticks_ms(), start_time))
    except: #////
        #//// save the traces to flash
        vl.save() 
        #/// log the traceback message
        vl.traceback(e)
        #/// update the thread status
        vl.thread_status(_thread_id, 'dead') 
        pycom.heartbeat(True)

    return acceleration
    

def loracom():
    global start_time

    #///// private variables to log the traces
    _thread_id = _thread.get_ident()
    _fun_name = 'loracom'
    _cls_name = '0'
    #//// update the thread status
    vl.thread_status(_thread_id, 'active') 

    try: #/////
        #print('thread 2:', _thread.get_ident())   
        
        #print('lora:', utime.ticks_diff(utime.ticks_ms(), start_time)) ### use ticks_diff only fordebugging
        #lock.acquire()
        data = str(control.readdata()[0])
        #//// logging
        vl.log(var='data', fun=_fun_name, clas=_cls_name, th=_thread_id)
        #print(data)
        #lock.release()
        ### create a LoRa socket
        s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        #//// logging
        vl.log(var='s', fun=_fun_name, clas=_cls_name, th=_thread_id)
        ### make the socket blocking
        ###(waits for the data to be sent and for the 2 receive windows to expire)
        s.setblocking(False)

        ### send some data
        s.send(data)
        print('Data sent')

        ### make the socket non-blocking
        ### (because if there's no data received it will block forever...)
        s.close()
        utime.sleep(2)
    except Exception: #/////
        #//// save the traces to flash
        vl.save()
        #/// log the traceback message
        vl.traceback(e)
        #//// update the thread status
        vl.thread_status(_thread_id, 'dead') 
        pycom.heartbeat(True)

class control:
    '''
    this class is used to communicate between threads and manage shared resources
    @classmethod: allows to pass the class as the argument, inturn allows to update the attributes of the class without creating the instance of the class
    '''
    sensor_data = []
    tx_flag = False   ### to indidcate transmission if loracom runs in seperate thread
    timer0_done = False ### flag to indicate timer had completed count to trigger other processes
    timer0 = Timer.Chrono()


    @classmethod
    def updatedata(cls, data):
        #///// private variables to log the traces
        _thread_id = _thread.get_ident()
        _fun_name = 'updatedata'
        _cls_name = cls.__name__

        ### update the sensor data in shared variable
        cls.sensor_data = [data]
        #//// logging
        vl.log(var='cls.sensor_data', fun=_fun_name, clas=_cls_name, th=_thread_id)
    
    @classmethod
    def readdata(cls):
        #///// private variables to log the traces
        _thread_id = _thread.get_ident()
        _fun_name = 'readdata'
        _cls_name = cls.__name__

        #//// logging
        vl.log(fun=_fun_name, clas=_cls_name, th=_thread_id) #//// as no variable in the function, this log should provide the trace when this function is called
        ### read the sensor data from shared variable
        return cls.sensor_data
    
    @classmethod
    def init_timer0(cls):
        #///// private variables to log the traces
        _thread_id = _thread.get_ident()
        _fun_name = 'init_timer0'
        _cls_name = cls.__name__

        ### initialize the timer object with duration equal to time
        #cls.timer0.init(Timer.ONE_SHOT, time, cls.sett0)
        #timer0 = Timer.Alarm(cls.sett0, time, periodic=False)  ### time in seconds, as no arguments passed to callback it passes the object itself
        cls.timer0.start()
        print('Timer Initialized')
        #print(cls.timer0.read_ms())  ### check

        #//// logging
        vl.log(fun=_fun_name, clas=_cls_name, th=_thread_id)
    
    @classmethod
    def read_timer0(cls):
        #///// private variables to log the traces
        _thread_id = _thread.get_ident()
        _fun_name = 'read_timer0'
        _cls_name = cls.__name__

        #//// logging
        vl.log(fun=_fun_name, clas=_cls_name, th=_thread_id)
        ### get the count of timer0 to check if it has completed counting (milliseconds)
        return cls.timer0.read_ms()
    
    @classmethod
    def reset_timer0(cls):
        #///// private variables to log the traces
        _thread_id = _thread.get_ident()
        _fun_name = 'reset_timer0'
        _cls_name = cls.__name__

        ### reset chrono timer
        cls.timer0.reset()

        #//// logging
        vl.log(fun=_fun_name, clas=_cls_name, th=_thread_id)
    
    @classmethod
    def stop_timer0(cls):
        #///// private variables to log the traces
        _thread_id = _thread.get_ident()
        _fun_name = 'stop_timer0'
        _cls_name = cls.__name__

        ### stop chrono timer
        cls.timer0.stop()

        #//// logging
        vl.log(fun=_fun_name, clas=_cls_name, th=_thread_id)



try:
    ### initialize it outside the scope of any function to allow access to all the code
    start_time = utime.ticks_ms()
    #/// update the thread status
    vl.thread_status('main', 'active') #//// update the thread status
    main_thread = _thread.start_new_thread(main, ())

    while True:
        ### check if threads are running
        ids, thread_info = vl.thread_status()
        
        status = [thread_info[x] for x in ids]
        #print(ids)
        #print(status)
        utime.sleep(2)

        ### enter REPL if main thread of application is dead
        if len(status) > 1:
            if status[-1] == 'dead':
                #//// save the data
                vl.save()
                ### log the error message
                pycom.heartbeat(True)
                #_thread.exit()
                #machine.reset()
               

except Exception as e:
    #//// save the data
    vl.save() 
    #/// log the traceback message
    vl.traceback(e)
    print('Error message:', e)
    pycom.heartbeat(True)