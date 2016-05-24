import sys
import os 
sys.path.append('src')

from Master import Master

m = Master(name = 'Server01', debug=True, destination_folder='Testing/Master')
m.setServer(host='localhost', port=8080)
m.setDelimeter(':::')
m.run()