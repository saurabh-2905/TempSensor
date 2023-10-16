import utime
import json
import os

class VarLogger:
    '''
    This class is the part of the tool, it logs data and collects all the information required to monitor the system
    all the code lines that are part of the tools are commented using '#/////'
    '''
    
    data = []   ### store variale sequence
    created_timestamp = utime.ticks_ms()  ### start time
    data_dict = {}  ### store timestamp for each variable
    _catchpop = 0  ### temporary storage
    _write_count = 0  ### count to track writing frequency

    ####### thread tracking
    threads_info = dict() ### init a dictionary to store the status of each thread

    @classmethod
    def log(cls, var='0', fun='0', clas='0', th='0'):
        '''
        var -> str = name of the variable
        '''
        dict_keys = cls.data_dict.keys()

        if var!=0 and var in dict_keys:
            _varlist = cls.data_dict[var]

            ### save only 500 latest values for each variable
            while len(_varlist) >= 500: 
                cls._catchpop = _varlist.pop(0)
            
            _varlist += [utime.ticks_ms()]
            cls.data_dict[var] = _varlist

        else:
            cls.data_dict[var] = [utime.ticks_ms()]

        ### make the event name based on the scope
        event = '{}_{}_{}_{}'.format(th, clas, fun, var)
        ### log the sequence to trace file
        cls.log_seq(event)
        
        cls._write_count +=1
        print(cls._write_count)
        ### write to flash approx every 6 secs (counting to 1000 = 12 ms)
        if cls._write_count >= 10:
            cls._write_count = 0
            cls.write_data() ### save the data to flash
                

    @classmethod
    def log_seq(cls, event):
        cls.data += [event]

    @classmethod
    def check_files(cls):
        '''
        check for previous log and update the name to avoid overwriting
        '''
        _files = os.listdir()
        _filename = 'log0'
        _seqname = 'trace0'

        for i in range(100):
            if _filename in _files:
                _filename = 'log{}'.format(i+1)
                _seqname = 'trace{}'.format(i+1)
            else:
                break

        return (_filename,_seqname)
    
    @classmethod
    def write_data(cls):
        write_name, trace_name = cls.check_files()  ### get the name to write the files and avoid overwriting previous log
        with open(write_name, 'w') as fp:
            json.dump(cls.data_dict, fp)
            print('dict saved', write_name)

        with open(trace_name, 'w') as fp:
            json.dump(cls.data, fp)
            print('trace saved', trace_name)

    @classmethod
    def thread_status(cls, thread_id=None, status=None):
        '''
        update or retrive the status of the thread. If no value is given to 'status' and 'thread_id' it will return the status of all the threads and it's ids
        status = ['dead' or 'alive']
        to update: pass arguments to thread_id and status
        to get status: dont pass andy arguments
        '''
        ### update status of the thread if it is active or not
        ids = cls.threads_info.keys()
        
        assert(status=='dead' or status=='active' or status==None)

        ### if status is given then update the status for respective thread
        if status!=None and thread_id!=None :
            cls.threads_info[thread_id] = status
        else:
            return(ids, cls.threads_info)