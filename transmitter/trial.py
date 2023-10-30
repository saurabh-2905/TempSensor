import sys
import utime
from lib.varlogger import VarLogger as vl
from machine import Timer

###### catch traceback #####
def trial():
    a = [1,2,3]

    try:
        print(a)
        print(a[3])
    except Exception as e:
        vl.traceback(e)
        
#trial()

##### test timer interrupt ######

class Clock():
    def start(self, time):
        '''
        time in ms
        '''
        self.alarm = Timer.Alarm(handler=self.cb, ms=time, periodic=True)

    def cb(self, alarm):
        #lock.acquire()
        #control.clock_set()
        #lock.release()
        print('clock done')

    def stop(self):
        self.alarm.cancel()
        print('clock stopped')