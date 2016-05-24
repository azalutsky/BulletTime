from os import listdir
from os.path import isfile, join, exists, abspath
from Networking import Client, Server
from Parameters import Parameters

class Master: 

    def __init__(self, name='', debug=False, destination_folder='Master'):
        self.name = name
        self.debug = debug
        self.client_list = []
        self.server = None
        self.destination_folder = destination_folder
        #self.param_file = Parameters(name=name, debug=debug)
        #self.folder_loc = folder_loc
        #self.writeParamHeaders()
        #self.writeParamFilenames()

    def __del__(self):
        if self.server:
            self.server.close()

    def setServer(self, host='localhost', port=8080):
        self.server = Server(host=host, port=port, debug=self.debug)

    def setDelimeter(self, delimeter=':::'):
        if self.server: 
            self.server.setDelimeter(delimeter)
        
    def run(self):
        self.server.run(self.destination_folder)

    def closeSlaves(self):
        for s in self.client_list:
            s.close()

    def resquestFolder(self):
        print "request"
        #requests folders in all 

    def remap(self, slave, filename):
        print "remap"
        #rename the file
