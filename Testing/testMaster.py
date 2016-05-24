import sys
import os 
import shutil
sys.path.append('src')

from Master import Master

if os.path.exists('Testing/Master'):
	shutil.rmtree('Testing/Master')

m = Master(name = 'Server01', debug=True, destination_folder='Testing/Master')
m.setServer(host='localhost', port=8080)
m.setDelimeter(':::')
m.run()