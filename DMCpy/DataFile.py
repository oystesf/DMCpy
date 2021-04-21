import h5py as hdf
import numpy as np
import pickle as pickle
import matplotlib.pyplot as plt
import pandas as pd

import os.path

import copy

class DataFile(object):
    def __init__(self, filePath=None):
        """DataFile object holding all data from a single DMC powder scan file

        Kwargs:

            - file (string or object): File path or file object (default None)

        If a file path is given data is loaded into this object. If an existing DataFile object
        is provided, its data is copied into the new object.

        """

        self._debugging = False

        if not filePath is None: 

            if isinstance(filePath,DataFile): # Copy everything from provided file
                # Copy all file settings
                self.updateProperty(filePath.__dict__)
                print('A DataFile Object was provided')

            elif os.path.exists(filePath): # load file from disk
                self.loadFile(filePath)
                print('file exists!')


            else:
                if not filePath == 'DEBUG': # If testing is activated load a dummy data file
                    raise FileNotFoundError('Provided file path "{}" not found.'.format(filePath))

                self._debugging = True
                self.folder = None
                self.fileName = None



        
    def loadFile(self,filePath):
        if not os.path.exists(filePath):
            raise FileNotFoundError('Provided file path "{}" not found.'.format(filePath))

        self.folder, self.fileName = os.path.split(filePath)


    def updateProperty(self,dictionary):
        """Update self with key and values from provided dictionary. Overwrites any properties already present."""
        if isinstance(dictionary,dict):
            for key in dictionary.keys():
                self.__setattr__(key,copy.deepcopy(dictionary[key]))
        else:
            raise AttributeError('Provided argument is not of type dictionary. Recieved instance of type {}'.format(type(dictionary)))


    def __eq__(self,other):
        return len(self.difference(other))==0


    def difference(self,other,keys = set(['fileName','folder'])):
        """Return the difference between two data files by keys"""
        dif = []
        if not set(self.__dict__.keys()) == set(other.__dict__.keys()): # Check if same generation and type (hdf or nxs)
            return list(set(self.__dict__.keys())-set(other.__dict__.keys()))

        comparisonKeys = keys
        for key in comparisonKeys:
            skey = self.__dict__[key]
            okey = other.__dict__[key]
            if isinstance(skey,np.ndarray):
                try:
                    if not np.all(np.isclose(skey,okey)):
                        if not np.all(np.isnan(skey),np.isnan(okey)):
                            dif.append(key)
                except (TypeError, AttributeError,ValueError):
                    if np.all(skey!=okey):
                        dif.append(key)
            elif not np.all(self.__dict__[key]==other.__dict__[key]):
                dif.append(key)
        return dif