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
        self._getData()

    def __delitem__(self,index):
        if index < len(self.dataFiles):
            del self.dataFiles[index]
        else:
            raise IndexError('Provided index {} is out of bounds for DataSet with length {}.'.format(index,len(self.dataFiles)))
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

    def plotInteractive(self,ax=None,masking=True,**kwargs):
        """Generate an interactive plot of data.

        Kwargs:

            - ax (axis): Matplotlib axis into which the plot is to be performed (default None -> new)

            - masking (bool): If true, the current mask in self.mask is applied (default True)

            - Kwargs: Passed on to errorbar or imshow depending on data dimensionality

        Returns:

            - ax: Interactive matplotlib axis

        """
        if ax is None:
            fig,ax = plt.subplots()
        else:
            fig = ax.get_figure()
        
        twoTheta = self.twoTheta

        # Find intensity
        intensityMatrix = np.divide(self.counts,self.normalization*self.monitor[:,np.newaxis,np.newaxis])
        

        if masking is True: # If masking, apply self.mask
            intensityMatrix[np.logical_not(self.mask)] = np.nan

        # Find plotting limits (For 2D pixel limits found later)
        thetaLimits = [f(twoTheta) for f in [np.min,np.max]]
        intLimits = [f(intensityMatrix) for f in [np.nanmin,np.nanmax]]

        # Copy relevant data to the axis
        ax.intensityMatrix = intensityMatrix
        ax.intLimits = intLimits
        ax.twoTheta = twoTheta
        ax.twoThetaLimits = thetaLimits
        ax.titles = [df.fileName for df in self]

        if ax.intensityMatrix.shape[-1] == 1: # Data is 1D, plot using errorbar
            # calculate errorbars
            ax.errorbarMatrix = np.divide(np.sqrt(self.counts),self.normalization*self.monitor[:,np.newaxis,np.newaxis])
            def plotSpectrum(ax,index=0,kwargs=kwargs):
                if kwargs is None:
                    kwargs = {}
                if hasattr(ax,'_sc'): # am errprbar has already been plotted, delete ot
                    ax._sc.remove()
                    del ax._sc
                
                if hasattr(ax,'color'): # use the color from previous plot
                    kwargs['color']=ax.color
                    
                # Plot data
                ax._sc = ax.errorbar(ax.twoTheta[index],ax.intensityMatrix[index],yerr=ax.errorbarMatrix[index].flatten(),**kwargs)
                ax.index = index # Update index and color
                ax.color = ax._sc.lines[0].get_color()
                # Set plotting limits and title
                ax.set_xlim(*ax.twoThetaLimits)
                ax.set_ylim(*ax.intLimits)
                ax.set_title(ax.titles[index])
                plt.draw()

            ax.set_ylabel('Inensity [arb]')
            
        else:
            # Find limits for y direction
            ax.pixelLimits = [f(self.pixelPosition[:,2]) for f in [np.nanmin,np.nanmax]]
            ax.pixelPosition = self.pixelPosition[:,2,:]

            def plotSpectrum(ax,index=0,kwargs=kwargs):
                # find color bar limits
                vmin,vmax = ax.intLimits
                extent = np.array([[f(dat) for f in [np.nanmin,np.nanmax]] for dat in [ax.twoTheta[index],ax.pixelPosition[index]]]).flatten()
                
                if hasattr(ax,'_imshow'):
                    ax._imshow.set_data(ax.intensityMatrix[index].T)
                    ax._imshow.set_extent(extent)
                else:
                    ax._imshow = ax.imshow(ax.intensityMatrix[index].T,extent=extent,origin='lower',vmin=vmin,vmax=vmax)

                
                ax.index = index
                if 'colorbar' in kwargs: # If colorbar attribute is given, use it
                    if kwargs['colorbar']: 
                        if not hasattr(ax,'_colorbar'): # If no colorbar is present, create one
                            ax._colorbar = fig.colorbar(ax._imshow,ax=ax)
                # Set limits
                ax.set_xlim(*ax.twoThetaLimits)
                ax.set_ylim(*ax.pixelLimits)
                ax.set_title(ax.titles[index])
                ax.set_aspect('auto')
                
                plt.draw()
                
            ax.set_ylabel('Inensity [arb]')

        # For all cases, x axis is two theta in degrees
        ax.set_xlabel(r'2$\theta$ [deg]')
        # Add function as method
        ax.plotSpectrum = lambda index,**kwargs: plotSpectrum(ax,index,**kwargs)
        
        # Plot first data point
        ax.plotSpectrum(0)

        ##### Interactivity #####

        def increaseAxis(self,step=1): # Call function to increase index
            index = self.index
            index+=step
            if index>=len(self.intensityMatrix):
                index = len(self.intensityMatrix)-1
            self.plotSpectrum(index)
            
        def decreaseAxis(self,step=1): # Call function to decrease index
            index = self.index
            index-=step
            if index<=-1:
                index = 0
            self.plotSpectrum(index)

        # Connect functions to key presses
        def onkeypress(self,event): # pragma: no cover
            if event.key in ['+','up']:
                increaseAxis(self)
            elif event.key in ['-','down']:
                decreaseAxis(self)
            elif event.key in ['home']:
                index = 0
                self.plotSpectrum(index)
            elif event.key in ['end']:
                index = len(self.intensityMatrix)-1
                self.plotSpectrum(index)
            elif event.key in ['pageup']: # Pressing pageup or page down performs steps of 10
                increaseAxis(self,step=10)
            elif event.key in ['pagedown']:
                decreaseAxis(self,step=10)

        # Call function for scrolling with mouse wheele
        def onscroll(self,event): # pragma: no cover
            if(event.button=='up'):
                increaseAxis(self)
            elif event.button=='down':
                decreaseAxis(self)
        # Connect function calls to slots
        fig.canvas.mpl_connect('key_press_event',lambda event: onkeypress(ax,event) )
        fig.canvas.mpl_connect('scroll_event',lambda event: onscroll(ax,event) )
        
        return ax


    def plotOverview(self,**kwargs):
        """Quick plotting of data set with interactive plotter and summed intensity.

        Kwargs:

            - masking (bool): If true, the current mask in self.mask is applied (default True)

            - kwargs (dict): Kwargs to be used for interactive or plotTwoTheta plot

        returns:

            - Ax (list): List of two axis, first containing the interactive plot, second summed two theta


        Kwargs for plotInteractiveKwargs:
        
            - masking (bool): Use generated mask for dataset (default True)

        Kwargs for plotTwoThetaKwargs:

            - twoThetaBins (array): Actual bins used for binning (default [min(twoTheta)-dTheta/2,max(twoTheta)+dTheta/2] in steps of dTheta=0.1 Deg)
            
            - applyNormalization (bool): Use normalization files (default True)
            
            - correctedTwoTheta (bool): Use corrected two theta for 2D data (default true)
        
        """

        fig,Ax = plt.subplots(2,1,figsize=(12,10))

        Ax = Ax.flatten()


        if not 'fmt' in kwargs:
            kwargs['fmt']='.-'

        if not 'masking' in kwargs:
            kwargs['masking']= True

        if not 'twoThetaBins' in kwargs:
            kwargs['twoThetaBins']= None

        if not 'applyNormalization' in kwargs:
            kwargs['applyNormalization']= True


        if not 'correctedTwoTheta' in kwargs:
            kwargs['correctedTwoTheta']= True

        if not 'colorbar' in kwargs:
            kwargs['colorbar']= False

        plotInteractiveKwargs = {}
        for key in ['masking','fmt','colorbar']:
            plotInteractiveKwargs[key] = kwargs[key]
        
        plotTwoThetaKwargs = {}
        for key in ['twoThetaBins','fmt','correctedTwoTheta','applyNormalization']:
            plotTwoThetaKwargs[key] = kwargs[key]

        ax2,*_= self.plotTwoTheta(ax=Ax[1],**plotTwoThetaKwargs)
        ax = self.plotInteractive(ax = Ax[0],**plotInteractiveKwargs)

        ax.set_xlabel('')
        ax2.set_title('Integrated Intensity')

        fig.tight_layout()
        return Ax