import sys,os
sys.path.append('.')
import pickle
import DMCpy

__version__ = '0.1.4'
__author__ = 'Jakob Lass'

installFolder = os.path.abspath(os.path.split(__file__)[0])
calibrationFile = os.path.join(installFolder,'data','calibrationDict.dat')
with open(calibrationFile,'rb') as f:
    calibrationDict = pickle.load(f)