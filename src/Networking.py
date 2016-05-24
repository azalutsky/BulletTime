import os
import socket
import string
import select
import sys
from shutil import copyfile
import re
import time

MAX_SEND_SIZE = 512

class Client:
    def __init__(self, port=8080, host='localhost', timeout=5, delimeter=':::', debug=False):
        self.port = port
        self.host = host
        self.timeout = timeout
        self.max_send_size = MAX_SEND_SIZE
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.debug = debug
        self.delimeter = delimeter
    
    def __del__(self):
        self.close()
    
    def sendParamFile(self, filename):
        if self.isConnected():
            cmd = "RequestFile" + str(self.delimeter) + str(filename)
            if self.debug:
                print "Command Sent: " + str(cmd)
            self.socket.send(cmd)

    def sendBinaryFile(self, filename):
        if self.isConnected():
            tmpfilename = filename+'.tmp'
            if self.debug:
                print "Sending file:" + str(filename)
            try: 
                copyfile(filename, tmpfilename)
                img = open(tmpfilename,'rb')
            except IOError as e: #handle other exceptions such as attribute errors
                print "Unexpected error:", e

            size = 0
            size = os.path.getsize(tmpfilename)
            print "Filesize: " + str(size)

        
            time.sleep(0.01)
            self.socket.send(str(size))
            time.sleep(0.01)
            
            while size > 0:
                size_of_send = size - self.max_send_size
                if size_of_send < 0:
                    size_of_send = size
                    size = size - size_of_send
                else:
                    size = size - self.max_send_size

                strng = img.read(size_of_send)
                self.socket.send(strng)

                if size <= 0:
                    break

            img.close()
            os.remove(tmpfilename)

            return True
        else:
            if self.debug:
                print "Not connected!"
            return False

        return True
            
    def isConnected(self):
        return self.connected
        
    def setDebug(self, debug):
        self.debug = debug
        
    def setPort(self, port):
        if self.debug: 
            print "Setting port: " + str(port)
        self.port = port

    def setHost(self, host):
        if self.debug: 
            print "Setting host: " + str(host)
        self.host = host

    def connect(self): 
        try:    
            self.socket.connect((self.host, self.port))
            self.connected = True
            if self.debug:
                print "Connection accepted"
            return True
        except:
            print "Client Error: " + str(sys.exc_info()[0])
            if self.debug:
                print "Couldn't connect"
        return False

    def run(self):
        while 1:
            data = self.socket.recv(self.max_send_size)
            if data:
                split_string = data.split(str(self.delimeter))
                function = split_string[0]
                function_data = split_string[1]

                if function == 'sendBinaryFile':
                    result = self.sendBinaryFile(function_data)
                elif function == 'closeClient':
                    result = self.close()
                    return False
                else:
                    print function 
                    print function_data
        return True


    def close(self):
        try: 
            self.socket.close()
            if self.debug and not self.isConnected():
                print "Connection closed"
            return True
        except: 
            if self.debug:
                print "Couldn't close" 
        return False

class Server:
    def __init__(self, port=8080, host='localhost', debug=False, timeout=5, delimeter=':::'):
        self.port = port
        self.host = host
        self.timeout = timeout
        self.RECV_BUFFER = MAX_SEND_SIZE
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = None
        self.delimeter = delimeter
        self.CONNECTION_LIST = []
        self.connection = None
        self.connected = False
        self.debug = debug
        self.setConnections()

    def setDelimeter(self, delimeter):
        self.delimeter = delimeter

    def setConnections(self):
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(self.timeout)
        self.CONNECTION_LIST.append(self.socket)

    def __del__(self):
        self.close()
        
    def recieveText(self):
        data = self.socket.recv(self.RECV_BUFFER)
        if self.debug:
            print "The following data was received - ",data
            print "Opening file - ",data
        fp = open(data,'r')
        strng = fp.read()
        size = os.path.getsize(data)
        size = str(size)
        self.socket.send(size)
        self.socket.send (strng)
    
    def receiveBinaryFile(self, sock, filename, location, remap=True):

        if not os.path.exists(location):
            os.makedirs(location)

        split_client_filename = string.split(filename,'/')
        if sys.platform == 'win32':
            split_client_filename = string.split(filename,'\\')

        source_folder = split_client_filename[-2]
        source_filename = split_client_filename[-1]

        if not os.path.exists(os.path.join(location,source_folder)):
            os.makedirs(os.path.join(location,source_folder))

        if remap: 
            #Get just the numbers and not the beginning text of the files
            source_filename_remap = re.search('(\d+.\w+)',source_filename)
            if source_filename_remap: 
                store_filename = os.path.abspath(os.path.join(location,source_folder,source_filename_remap.group(0)))
        else:
            store_filename = os.path.abspath(os.path.join(location,source_folder,source_filename))

        #check if file exists - delete if it does.
        if os.path.isfile(store_filename):
            os.rename(store_filename, store_filename + '.old')

        #try:
        if self.debug: 
            print "Recieving: " + str(os.path.abspath(filename))
            print "Storing: " + str(store_filename)

        cmd = 'sendBinaryFile' + str(self.delimeter) + str(os.path.abspath(filename))

        sock.send(cmd)

        fp = open(store_filename,'wb')

        
        time.sleep(0.01)
        size = int(sock.recv(self.RECV_BUFFER))
        time.sleep(0.01)

        while size > 0:
            size_of_recv = size - self.RECV_BUFFER
            if size_of_recv < 0:
                size_of_recv = size
                size = size - size_of_recv
            else:
                size_of_recv = self.RECV_BUFFER
                size = size - self.RECV_BUFFER

            strng = sock.recv(self.RECV_BUFFER)
            fp.write(strng)

            if size <= 0:
                break

        fp.close()
        return True
        #except:
        #    print "Failed to Recieve: " + str(sys.exc_info()[0])
        #    return False
            
    def sendBinaryFile(self, filename):
        if self.debug:
            print "Sending file - ",data
        img = open(filename,'rb')
        while True:
            strng = img.readline(self.RECV_BUFFER)
            if not strng:
                break
            self.connection.send(strng)
        img.close()
        if self.debug:
            print "Data sent successfully"
    
    def isConnected(self):
        return self.connected
        
    def setDebug(self, debug):
        self.debug = debug
        
    def setPort(self, port):
        if self.debug: 
            print "Setting port: " + str(port)
        self.port = port

    def setHost(self, host):
        if self.debug: 
            print "Setting host: " + str(host)
        self.host = host

    def run(self, destination_folder='Master'): 
        while 1:
            # Get the list sockets which are ready to be read through select
            read_sockets,write_sockets,error_sockets = select.select(self.CONNECTION_LIST,[],[])

            for sock in read_sockets:

                #New connection
                if sock == self.socket:
                    # Handle the case in which there is a new connection recieved through server_socket
                    sockfd, addr = sock.accept()
                    self.CONNECTION_LIST.append(sockfd)
                    print "Client (%s, %s) connected" % addr
                     
                #Some incoming message from a client
                else:
                    # Data recieved from client, process it
                # try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(self.RECV_BUFFER)

                    # echo back the client message
                    if data:

                        data_map = data.split( str(self.delimeter) )
                        print data_map
                        function = data_map[0]
                        function_data = data_map[1]

                        if function == 'RequestFile':

                            data_type = function_data.split('.')[-1]

                            self.receiveBinaryFile(sock, function_data, destination_folder, remap=False)

                            file_split = string.split(function_data,'/')
                            if sys.platform == 'win32':
                                file_split = string.split(function_data,'\\')
                                
                            folder_split = file_split[-2]
                            filename_split = file_split[-1]

                            param_filename = os.path.abspath(os.path.join(destination_folder,folder_split,filename_split))

                            print param_filename

                            if data_type == 'param':
                                file_list = self.getParamFileList(param_filename)
                                self.getFiles(sock, file_list, destination_folder)

                            self.closeClient(sock)
            if len(self.CONNECTION_LIST) == 1:
                self.close()
                return True
        return True

    def closeClient(self, sock):
        print "Closing Client"
        sock.send("closeClient" + self.delimeter + "True")
        self.CONNECTION_LIST.remove(sock)


    def getFiles(self, sock, file_list, destination_folder='Master'):
        print "Getting " + str(len(file_list)) + " files"

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        for f in file_list:
            f = f.rstrip()
            res = self.receiveBinaryFile(sock, f, destination_folder)
            if res:
                print "File " + f + " sent successfully."

    def getParamFileList(self, file_loc):
        file_list = []
        fp = open(file_loc,'rb')
        while True:
            strng = fp.readline(self.RECV_BUFFER)
            if not strng:
                break
            strng_split = strng.split( str(self.delimeter) )
            if strng_split[0] == "File":
                file_list.append(strng_split[1])

        fp.close()
        return file_list

    def close(self):
        try: 
            self.socket.close()
            if self.debug:
                print "Connection closed"
            return True
        except: 
            if self.debug:
                print "Couldn't close" 
        return False
