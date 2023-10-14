import utime
import json
import os

class VarLogger:
    def __init__(self):
        self.data = []   ### store variale sequence
        self.created_timestamp = utime.ticks_ms()  ### start time
        self.data_dict = {}  ### store timestamp for each variable
        self._catchpop = 0  ### temporary storage
        self._write_count = 0  ### count to track writing frequency
        self.write_name, self.trace_name = self.check_files()  ### avoid overwriting previous log


    def log(self, var, fun='fun', clas='cls', th='th'):
        '''
        var -> str = name of the variable
        '''
        dict_keys = self.data_dict.keys()

        if var in dict_keys:
            _varlist = self.data_dict[var]

            ### save only 500 latest values for each variable
            while len(_varlist) >= 500: 
                self._catchpop = _varlist.pop(0)
            
            _varlist += [utime.ticks_ms()]
            self.data_dict[var] = _varlist

        else:
            self.data_dict[var] = [utime.ticks_ms()]

        ### make the event name based on the scope
        event = f'{th}_{clas}_{fun}_{var}'
        ### log the sequence to trace file
        self.log_seq(event)
        
        self._write_count +=1
        print(self._write_count)

        ### write to flash approx every 6 secs (counting to 1000 = 12 ms)
        if self._write_count >= 10:
            self._write_count = 0
            with open(self.write_name, 'w') as fp:
                json.dump(self.data_dict, fp)
                print('dict saved', self.write_name)

            with open(self.trace_name, 'w') as fp:
                json.dump(self.data, fp)
                print('trace saved', self.trace_name)
                

    
    def log_seq(self, event):
        self.data += [event]


    def check_files(self):
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