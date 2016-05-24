from os.path import isfile, join, exists, abspath
from os import makedirs
import os

class Parameters:
    def __init__(self, name, debug=False, destination='Params', file_type='.param'):
        self.name = name
        self.param_file = None
        self.param_file_open = False
        self.debug = debug
        self.destination = destination
        self.file_type = file_type
        self.param_path = ''
        self.create()
        
    def __del__(self):
        self.close()
    
    def getDestination(self):
        return self.destination
        
    def getFileType(self):
        return self.file_type
        
    def create(self):
        if not exists(abspath(self.destination)):
            makedirs(abspath(self.destination))
            if self.debug: 
                print "Directory doesnt exists, making: " + str(abspath(self.destination))
        self.param_path = abspath(join(self.destination,self.name+self.file_type))
        if self.debug:
            print "Parameter path: " + str(self.param_path)
        try: 
            self.param_file = open(self.param_path,'w')
            self.param_file_open = True
        except: 
            if self.debug: 
                print "Failed to create Parameters file for " + str(self.name)
                
    def write(self, txt):
        self.param_file.write(txt)
        
    def close(self):
        self.param_file.close()
        
