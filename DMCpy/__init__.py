import sys,os
sys.path.append('.')
import pickle
import DMCpy

__version__ = '0.1.4'
__author__ = 'Jakob Lass'

installFolder = os.path.abspath(os.path.split(__file__)[0])
calibrationFile = os.path.join(installFolder,'data','calibrationDict.dat')
try:
    with open(calibrationFile,'rb') as f:
        calibrationDict = pickle.load(f)
except FileNotFoundError:
    import glob

    print("Contents of local folder is: {}".format(os.listdir(installFolder)))
    if not os.path.exists(os.path.join(installFolder,'data')):
        print('The data path does not exist..')
    else:
        print('Contents of data path is: {}'.format(os.listdir(os.path.join(installFolder,'data'))))
    print('Content of parent folder is: {}'.format(os.listdir(os.path.join(installFolder,'..'))))