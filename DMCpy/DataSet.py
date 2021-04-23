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
            
            self._getData()

    def _getData(self):
        # Collect parameters listed below across data files into self
        for parameter in ['counts','monitor','twoTheta','correctedTwoTheta','fileName','pixelPosition','waveLength','mask']:
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


    def generateMask(self,maskingFunction = DataFile.maskFunction, **pars):
        """Generate maks to applied to data in data file
        
        Kwargs:

            - maskingFunction (function): Function called on self.phi to generate mask (default maskFunction)

        All other arguments are passed to the masking function.

        """
        for d in self:
            d.generateMask(maskingFunction,**pars)
        self._getData()

    def sumDetector(self,thetaStart=None,thetaStop=None,dTheta=0.1,corrected=True):
        """Find intensity as function of either twoTheta or correctedTwoTheta

        Kwargs:

            - thetaStart (float): Start of twoTheta plot in degrees (default minimum of all two thetas)

            - thetaStop (float): Stop of twoTheta plot in degrees (default maximum of all two thetas)

            - dTheta (float): Step size in twoTheta in degrees (default 0.1)

            - corrected (bool): If true, use corrected two theta, otherwise sum vertically on detector (default True)

        Returns:

            - twoTheta
            
            - Normalized Intensity
            
            - Normalized Intensity Error

        """

        if corrected:
            twoTheta = self.correctedTwoTheta
        else:
            twoTheta = self.twoTheta


        if thetaStart is None:
            anglesMin = np.min(twoTheta)
        else:
            anglesMin = thetaStart

        if thetaStart is None:
            anglesMax = np.max(twoTheta)
        else:
            anglesMax = thetaStop
            
        

        error = np.sqrt(self.counts)

        monitorRepeated = np.repeat(np.repeat(self.monitor[:,np.newaxis,np.newaxis],400,axis=1),self.counts.shape[2],axis=2)


        intensity = self.counts/monitorRepeated

        twoThetaBins = np.arange(anglesMin-0.5*dTheta,anglesMax+0.51*dTheta,dTheta)

        summedRawIntenisty, _ = np.histogram(twoTheta[self.mask],bins=twoThetaBins,weights=self.counts[self.mask])
        summedIntensity, _ = np.histogram(twoTheta[self.mask],bins=twoThetaBins,weights=intensity[self.mask])
        summedMonitor, _ = np.histogram(twoTheta[self.mask],bins=twoThetaBins,weights=monitorRepeated[self.mask])
        

        inserted, _  = np.histogram(twoTheta[self.mask],bins=twoThetaBins)

        normalizedIntensity = summedRawIntenisty/summedMonitor
        normalizedIntensityError =  np.sqrt(summedRawIntenisty)/summedMonitor

        return twoThetaBins, normalizedIntensity, normalizedIntensityError
    

    def plotTwoTheta(self,ax=None,thetaStart=None,thetaStop=None,dTheta=0.1,corrected=True,**kwargs):
        """Plot intensity as function of correctedTwoTheta or twoTheta

        Kwargs:

            - ax (axis): Matplotlib axis into which data is plotted (default None - generates new)

            - thetaStart (float): Start of twoTheta plot in degrees (default minimum of all two thetas)

            - thetaStop (float): Stop of twoTheta plot in degrees (default maximum of all two thetas)

            - dTheta (float): Step size in twoTheta in degrees (default 0.1)

            - corrected (bool): If true, use corrected two theta, otherwise sum vertically on detector (default True)

            - All other key word arguments are passed on to plotting routine

        Returns:

            - ax: Matplotlib axis into which data was plotted

        """
        
        
        twoThetaBins, normalizedIntensity, normalizedIntensityError = self.sumDetector(thetaStart=thetaStart,thetaStop=thetaStop,dTheta=dTheta,corrected=corrected)

        TwoThetaPositions = 0.5*(twoThetaBins[:-1]+twoThetaBins[1:])

        if not 'fmt' in kwargs:
            kwargs['fmt'] = '-.'

        if ax is None:
            fig,ax = plt.subplots()

        ax.errorbar(TwoThetaPositions,normalizedIntensity,yerr=normalizedIntensityError,**kwargs)
        ax.set_xlabel(r'$2\theta$ [deg]')
        ax.set_ylabel(r'Intensity [arb]')

        return ax
