import h5py as hdf
import numpy as np
import pickle as pickle
import matplotlib.pyplot as plt
import pandas as pd

from DMCpy import DataFile, _tools


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
        for parameter in ['counts','monitor','twoTheta','correctedTwoTheta','fileName','pixelPosition','waveLength','mask','normalization','normalizationFile','time']:
            setattr(self,parameter,np.array([getattr(d,parameter) for d in self]))

        # Collect parameters from sample into self
        for parameter in ['sample_temperature','sample_name']:
            setattr(self,parameter,np.array([getattr(d.sample,parameter) for d in self]))


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

    def append(self,item):
        try:
            if isinstance(item,(str,DataFile.DataFile)): # A file path or DataFile has been provided
                item = [item]
            [self.dataFiles.append(f) for f in item]
        except Exception as e:
            raise(e)
        self._getData


    def generateMask(self,maskingFunction = DataFile.maskFunction, **pars):
        """Generate maks to applied to data in data file
        
        Kwargs:

            - maskingFunction (function): Function called on self.phi to generate mask (default maskFunction)

        All other arguments are passed to the masking function.

        """
        for d in self:
            d.generateMask(maskingFunction,**pars)
        self._getData()

    @_tools.KwargChecker()
    def sumDetector(self,twoThetaBins=None,applyNormalization=True,correctedTwoTheta=True):
        """Find intensity as function of either twoTheta or correctedTwoTheta

        Kwargs:

            - twoThetaBins (list): Bins into which 2theta is to be binned (default min(2theta),max(2theta) in steps of 0.1)

            - applyNormalization (bool): If true, take detector efficiency into account (default True)

            - correctedTwoTheta (bool): If true, use corrected two theta, otherwise sum vertically on detector (default True)

        Returns:

            - twoTheta
            
            - Normalized Intensity
            
            - Normalized Intensity Error

            - Total Monitor

        """

        if correctedTwoTheta:
            twoTheta = self.correctedTwoTheta
        else:
            twoTheta = self.twoTheta


        if twoThetaBins is None:
            anglesMin = np.min(twoTheta)
            anglesMax = np.max(twoTheta)
            dTheta = 0.1
            twoThetaBins = np.arange(anglesMin-0.5*dTheta,anglesMax+0.51*dTheta,dTheta)

        

        monitorRepeated = np.repeat(np.repeat(self.monitor[:,np.newaxis,np.newaxis],400,axis=1),self.counts.shape[2],axis=2)

        

        summedRawIntenisty, _ = np.histogram(twoTheta[self.mask],bins=twoThetaBins,weights=self.counts[self.mask])

        if applyNormalization:
            summedMonitor, _ = np.histogram(twoTheta[self.mask],bins=twoThetaBins,weights=monitorRepeated[self.mask]*self.normalization[self.mask])
        else:
            summedMonitor, _ = np.histogram(twoTheta[self.mask],bins=twoThetaBins,weights=monitorRepeated[self.mask])

        inserted, _  = np.histogram(twoTheta[self.mask],bins=twoThetaBins)

        normalizedIntensity = summedRawIntenisty/summedMonitor
        normalizedIntensityError =  np.sqrt(summedRawIntenisty)/summedMonitor

        return twoThetaBins, normalizedIntensity, normalizedIntensityError,summedMonitor
    

    @_tools.KwargChecker(function=plt.errorbar,include=_tools.MPLKwargs)
    def plotTwoTheta(self,ax=None,twoThetaBins=None,applyNormalization=True,correctedTwoTheta=True,**kwargs):
        """Plot intensity as function of correctedTwoTheta or twoTheta

        Kwargs:

            - ax (axis): Matplotlib axis into which data is plotted (default None - generates new)

            - twoThetaBins (list): Bins into which 2theta is to be binned (default min(2theta),max(2theta) in steps of 0.1)

            - applyNormalization (bool): If true, take detector efficiency into account (default True)

            - correctedTwoTheta (bool): If true, use corrected two theta, otherwise sum vertically on detector (default True)

            - All other key word arguments are passed on to plotting routine

        Returns:

            - ax: Matplotlib axis into which data was plotted

            - twoThetaBins
            
            - normalizedIntensity
            
            - normalizedIntensityError

        """
        
        
        twoThetaBins, normalizedIntensity, normalizedIntensityError,summedMonitor = self.sumDetector(twoThetaBins=twoThetaBins,applyNormalization=applyNormalization,\
                                                                                       correctedTwoTheta=correctedTwoTheta)

        TwoThetaPositions = 0.5*(twoThetaBins[:-1]+twoThetaBins[1:])

        if not 'fmt' in kwargs:
            kwargs['fmt'] = '-.'

        if ax is None:
            fig,ax = plt.subplots()

        ax.errorbar(TwoThetaPositions,normalizedIntensity,yerr=normalizedIntensityError,**kwargs)
        ax.set_xlabel(r'$2\theta$ [deg]')
        ax.set_ylabel(r'Intensity [arb]')

        return ax,twoThetaBins, normalizedIntensity, normalizedIntensityError,summedMonitor
