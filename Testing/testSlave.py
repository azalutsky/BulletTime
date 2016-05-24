import sys
import os 
sys.path.append('src')
from Slave import Slave
import shutil
 
def copyDirectory(src, dest):
    try:
        shutil.copytree(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print('Directory not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('Directory not copied. Error: %s' % e)

copyDirectory('Testing/TestImages', 'Testing/TestImagesTmp')
s0 = Slave(name = 'Slave01', folder_loc='Testing/TestImagesTmp/Ingest_02', host='localhost', port=8080, debug=True)