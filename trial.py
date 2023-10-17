import sys
import utime
from lib.varlogger import VarLogger as vl

def trial():
    a = [1,2,3]

    try:
        print(a)
        print(a[3])
    except Exception as e:
        vl.traceback(e)
        
trial()