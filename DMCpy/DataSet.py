import h5py as hdf
import numpy as np
import pickle as pickle
import matplotlib.pyplot as plt
import pandas as pd

from DMCpy import DataFile


class DataSet(object):
    def __init__(self, dataFiles=None,**kwargs):
        """DataSet object to hold a series of DataFile objects

        Kwargs:

            - dataFiles (list): List of data files to be used in reduction (default None)

        Raises:

            - NotImplemetedError

            - AttributeError

        """

        if dataFiles is None:
            self.dataFiles = []
        else:
            if isinstance(dataFiles,(str,DataFile.DataFile)): # If either string or DataFile instance wrap in a list
                dataFiles = [dataFiles]
            try:
                self.dataFiles = [DataFile.DataFile(dF) for dF in dataFiles]
            except TypeError:
                raise AttributeError('Provided dataFiles attribute is not itterable, filepath, or of type DataFile. Got {}'.format(dataFiles))
            
            # Collect parameters listed below across data files into self
            for parameter in ['counts','monitor','twoTheta','correctedTwoTheta','fileName','pixelPosition','waveLength']:
                setattr(self,parameter,np.array([getattr(d,parameter) for d in self]))


    def __len__(self):
        """return number of DataFiles in self"""
        return len(self.dataFiles)
        

    def __eq__(self,other):
        """Check equality to another object. If they are of the same class (DataSet) and have the same attribute keys, the compare equal"""
        return np.logical_and(set(self.__dict__.keys()) == set(other.__dict__.keys()),self.__class__ == other.__class__)


    def __getitem__(self,index):
        try:
            return self.dataFiles[index]
        except IndexError:
            raise IndexError('Provided index {} is out of bounds for DataSet with length {}.'.format(index,len(self)))

    def __len__(self):
        return len(self.dataFiles)
    
    def __iter__(self):
        self._index=0
        return self
    
    def __next__(self):
        if self._index >= len(self):
            raise StopIteration
        result = self.dataFiles[self._index]
        self._index += 1
        return result

    def next(self):
        return self.__next__()
    

    def plotTwoTheta(self,ax=None,thetaStart=None,thetaStop=None,dTheta=0.1,**kwargs):
        """Plot intensity as function of correctedTwoTeha

        Kwargs:

            - ax (axis): Matplotlib axis into which data is plotted (default None - generates new)

            - thetaStart (float): Start of twoTheta plot in degrees (default minimum of all two thetas)

            - thetaStop (float): Stop of twoTheta plot in degrees (default maximum of all two thetas)

            - dTheta (float): Step size in twoTheta in degrees (default 0.1)

            - All other key word arguments are passed on to plotting routine

        Returns:

            - ax: Matplotlib axis into which data was plotted

        """
        
        if thetaStart is None:
            anglesMin = np.min(self.correctedTwoTheta)
        else:
            anglesMin = thetaStart

        if thetaStart is None:
            anglesMax = np.max(self.correctedTwoTheta)
        else:
            anglesMax = thetaStop
            
        

        error = np.sqrt(self.counts)

        monitorRepeated = np.repeat(np.repeat(self.monitor[:,np.newaxis,np.newaxis],400,axis=1),self.counts.shape[2],axis=2)


        intensity = self.counts/monitorRepeated

        twoThetaBins = np.arange(anglesMin-0.5*dTheta,anglesMax+0.51*dTheta,dTheta)

        summedRawIntenisty, _ = np.histogram(self.correctedTwoTheta.flatten(),bins=twoThetaBins,weights=self.counts.flatten())
        summedIntensity, _ = np.histogram(self.correctedTwoTheta.flatten(),bins=twoThetaBins,weights=intensity.flatten())
        summedMonitor, _ = np.histogram(self.correctedTwoTheta.flatten(),bins=twoThetaBins,weights=monitorRepeated.flatten())
        

        inserted, _  = np.histogram(self.correctedTwoTheta.flatten(),bins=twoThetaBins)

        normalizedIntensity = summedRawIntenisty/summedMonitor
        normalizedIntensityError =  np.sqrt(summedRawIntenisty)/summedMonitor


        TwoThetaPositions = 0.5*(twoThetaBins[:-1]+twoThetaBins[1:])

        if not 'fmt' in kwargs:
            kwargs['fmt'] = '-.'

        fig,ax = plt.subplots()
        ax.errorbar(TwoThetaPositions,normalizedIntensity,yerr=normalizedIntensityError,**kwargs)
        ax.set_xlabel(r'$2\theta$ [deg]')
        ax.set_ylabel(r'Intensity [arb]')

        return ax
