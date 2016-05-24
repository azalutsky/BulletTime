Project Name: 
	BulletTime Networking Tool
	Anton Zalutsky

Installation:

	Required: 
		Python 2.6 or greater, but below 3.0

Overview: 

	This software will push a Client's folder of data to a Master on the network. 

Testing: 
	
	There are two files: testMaster.py and testSlave.py 

	Open two terminals. 

	Terminal 1: 
		>> cd [file path of this folder]
		>> python testMaster.py

	Terminal 2: 
		>> cd [file path of this folder]
		>> python testSlave.py

	testMaster.py is creating a server and the main repository of where files will be stored. 
		m = Master(name = 'Server01', debug=True, destination_folder='MasterFiles')
		m.setServer(host='localhost', port=8080)
		m.run()

		name: the name we will call the Master. 
		debug: saying I want to output to the terminal what its doing.
		destination_folder: folder we would like to save our picture files 
		host: our host IP address
		port: our host port address

	testSlave.py is creating a Param folder. This will host important information about the files we have stored. 
		s0 = Slave(name = 'Slave01', folder_loc='TestImageClient', host='localhost', port=8080, debug=True)

		name: the name we will call this Slave
		folder_loc: the source of the images we want to push to the Master.
		host: our host IP address
		port: our host port address
		debug: saying I want to output to the terminal what its doing.

	testSlave.py will then send the Param file it creates to testMaster.py 
	Once it does that, testMaster.py can read it and request files in a directory we established as TestImageClient with two images. 
	It pushes the files all into MasterFiles.

	Changing 'localhost' to the server's IP address on a local network should work as well.

