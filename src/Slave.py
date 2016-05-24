from os import listdir, walk, makedirs, rename, rmdir, remove
from os.path import isfile, join, exists, abspath, relpath, isfile
from Networking import Client
from Parameters import Parameters
from FolderParser import Folder, File, FolderParser
import time

class Slave: 
    def __init__(self, name, index=1, host='localhost', port=8080, debug=False, param_file=None, folder_loc='', delimeter=':::', cameras=12, acceptable_filetype_set=['.JPG','CR2'], destination=None):
        self.name = name
        self.debug = debug
        self.index = index
        self.port = port
        self.host = host
        self.delimeter = delimeter
        self.client = Client(host=host, port=port, debug=debug, delimeter=self.delimeter)
        self.param_file = param_file
        if self.param_file:
            self.writeParamHeaders()
            self.writeParamFilenames()
            self.closeParam()


        #functions that revolve around other instances
        self.cameras=cameras
        self.acceptable_filetype_set=acceptable_filetype_set

        self.folder_loc = folder_loc
        self.folder = Folder(self.folder_loc)
        self.checkFolders()

        self.client.connect()

    def __del__(self): 
        if self.client:
            self.client.close()
        
    '''Param File Helper Functions'''
    def setParameters(self, name, destination):
        self.param_file = Parameters(name=self.name,destination=destination)
        self.writeParamHeaders()
        self.writeParamFilenames()
        self.closeParam()

    def writeParamHeaders(self):
        #if self.debug: 
        #    print "writeHeaders" 
        self.param_file.write("Name" + str(self.delimeter) + str(self.name) + "\n")
        self.param_file.write("Port" + str(self.delimeter) + str(self.port) + "\n")
        self.param_file.write("Host" + str(self.delimeter) + str(self.host) + "\n")
        self.param_file.write("Parameter File Location" + str(self.delimeter) + str(abspath(join(self.param_file.getDestination(), self.name + self.param_file.getFileType()))) + "\n")
    
    def writeParamFilenames(self): 
        #if self.debug:
        #    print "writeParamFilenames"
        file_list = self.getFilenames(self.folder)

        for f in file_list:
            self.param_file.write("File" + str(self.delimeter) + str(f) + "\n")
    
    def closeParam(self):
        self.param_file.close()

    def setFolderLocation(self, folder_loc):
        self.folder_loc = folder_loc
            
    def getFilenames(self, folder, file_list=[]):
        for file in folder.files:
            if file.type.upper() in self.acceptable_filetype_set:
                file_list.append(file.path)
        for folder in folder.folders: 
            file_list = self.getFilenames(folder=folder, file_list=file_list)
        return file_list

    def getFilenamesFolders(self, folder, folder_list=[]):
        for file in folder.files:
            if file.type.upper() in self.acceptable_filetype_set:
                if folder not in folder_list:
                    folder_list.append(folder)
        for folder in folder.folders: 
            file_list = self.getFilenamesFolders(folder=folder, folder_list=folder_list)
        return folder_list

    def checkData(self, folder, bad_data=[]):
        data_ok = True
        for data_type in self.acceptable_filetype_set:
            count_types = 0
            for file in folder.files:
                if file.type.upper() == data_type:
                    count_types += 1
            if (count_types != self.cameras) and (count_types > 0): 
                if [count_types, folder.path] not in bad_data:
                    data_ok = False
                    bad_data.append([count_types, folder.path])
        for folder in folder.folders: 
            self.checkData(folder=folder, bad_data=bad_data)
        return bad_data

    def moveTree(self, sourceRoot, destRoot):
        if not exists(destRoot):
            return False
        ok = True
        for path, dirs, files in walk(sourceRoot):

            relPath = relpath(path, sourceRoot)
            destPath = join(destRoot, relPath)
            if not exists(destPath):
                makedirs(destPath)
            for file in files:
                destFile = join(destPath, file)
                if isfile(destFile):
                    print "Skipping existing file: " + join(relPath, file)
                    remove(join(sourceRoot, file))
                    ok = False
                    continue
                srcFile = join(path, file)
                #print "rename", srcFile, destFile
                rename(srcFile, destFile)
        for path, dirs, files in walk(sourceRoot, False):
            if len(files) == 0 and len(dirs) == 0:
                rmdir(path)
        return ok

    def checkFolders(self):
        folders = self.getFilenamesFolders(self.folder)
        for folder in folders:
            bad_data = self.checkData(folder)
        while bad_data != []:
            if (len(bad_data)%2 == 0):
                print "Data problem in two folders..."
                data_set_1 = bad_data.pop()
                data_set_2 = bad_data.pop()
                size_of_datas = data_set_1[0]+data_set_2[0]
                if size_of_datas == self.cameras: 
                    print "Data appears to be fixable..."
                    self.moveTree(data_set_1[1], data_set_2[1])
                    print "Files moved, problem resolved between: " 
                    print data_set_1[1] 
                    print data_set_2[1]
            else: 
                print "Corrupt folders are not aligned... Please manually inspect them."
        self.folder = Folder(self.folder_loc)
                
    def run(self):

        self.client.sendParamFile(self.param_file.param_path)
        self.client.run()
        self.client.close()
        