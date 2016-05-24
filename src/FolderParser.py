import os, time 

def getPathExtension(path):
	filename, file_extension = os.path.splitext(path)
	return file_extension

def getPathBasename(path):
	basename = os.path.basename(path)
	return basename

def getPathCreationDate(path):
	creation_date = time.ctime(os.path.getctime(path))
	return creation_date 

class File:
	def __init__(self, path, root=None):
		self.path = path
		self.root = root
		self.type = getPathExtension(self.path)
		self.name = getPathBasename(self.path)
		self.time = getPathCreationDate(self.path)
	def getRoot(self):
		return self.root
	def getPath(self):
		return self.path
	def getType(self):
		return self.type
	def getName(self):
		return self.name
	def getTime(self):
		return self.time

class Folder: 
	def __init__(self, path, root=None): 
		self.files = []
		self.folders = []
		self.root = root
		self.path = path 
		self.name = getPathBasename(path)
		self.walk()
	def getRoot(self):
		return self.root
	def getPath(self):
		return self.path
	def getName(self):
		return self.name
	def walk(self): 
		directory = next(os.walk(self.path))
		root = directory[0] 
		dirs = directory[1]
		files = directory[2] 
		for dir in dirs:
			self.folders.append(Folder(os.path.join(root,dir), root=root))
		for file in files:
			self.files.append(File(os.path.join(root,file), root=root))

class FolderParser: 
	def __init__(self, root, delimeter='-', indent='\t'): 
		if not os.path.exists(root):
			print "Path does not exist, exitting."
			return
		self.tree = Folder(root)
		self.root = root
		self.delimeter = delimeter
		self.indent = indent

	def printStructure(self, folder=None, indent_count=0):
		if folder==None:
			print self.root

			folder=self.tree
		indent = self.indent*indent_count

		for file in folder.files: 
			print str(indent) + str(self.delimeter) + str(file.name)
		for folder in folder.folders:
			print str(indent) + str(self.delimeter) + str(folder.name) 
			self.printStructure(folder=folder, indent_count=indent_count+1)

