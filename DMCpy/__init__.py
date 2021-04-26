import sys,os
sys.path.append('.')
import pickle

__version__ = '0.1.4'
__author__ = 'Jakob Lass'



calibrationFile = os.path.join(sys.prefix,'DMCpy','data','calibrationDict.dat')
with open(calibrationFile,'rb') as f:
    calibrationDict = pickle.load(f)