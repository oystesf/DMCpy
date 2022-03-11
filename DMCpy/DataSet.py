import h5py as hdf
import numpy as np
import pickle as pickle
import matplotlib.pyplot as plt
import pandas as pd
import os
from DMCpy import DataFile, _tools, Viewer3D


class DataSet(object):
    def __init__(self, dataFiles=None,**kwargs):
        """DataSet object to hold a series of DataFile objects

        Kwargs:

            - dataFiles (list): List of data files to be used in reduction (default None)

        Raises:

            - NotImplementedError

            - AttributeError

        """

        if dataFiles is None:
            self.dataFiles = []
        else:
            if isinstance(dataFiles,(str,DataFile.DataFile)): # If either string or DataFile instance wrap in a list
                dataFiles = [dataFiles]
            try:
                self.dataFiles = [DataFile.loadDataFile(dF) if isinstance(dF,(str)) else dF for dF in dataFiles]
            except TypeError:
                raise AttributeError('Provided dataFiles attribute is not iterable, filepath, or of type DataFile. Got {}'.format(dataFiles))
            
            self._getData()

    def _getData(self):
        # Collect parameters listed below across data files into self
        for parameter in ['counts','monitor','twoTheta','correctedTwoTheta','fileName','pixelPosition','waveLength','mask','normalization','normalizationFile','time','temperature']:
            setattr(self,parameter,np.array([getattr(d,parameter) for d in self]))

        
        types = [df.fileType for df in self]
        if len(types)>1:
            if not np.all([types[0] == t for t in types[1:]]):
                raise AttributeError('Provided data files have different types!\n'+'\n'.join([df.fileName+': '+df.scanType for df in self]))
        self.type = types[0]


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
            for f in item:
                if isinstance(f,str):
                    f = DataFile.loadDataFile(f)
                self.dataFiles.append(f)
        except Exception as e:
            raise(e)
        self._getData()

    def __delitem__(self,index):
        if index < len(self.dataFiles):
            del self.dataFiles[index]
        else:
            raise IndexError('Provided index {} is out of bounds for DataSet with length {}.'.format(index,len(self.dataFiles)))
        self._getData


    @property
    def sample(self):
        return [df.sample for df in self]

    @sample.getter
    def sample(self):
        return [df.sample for df in self]

    @sample.setter
    def sample(self,sample):
        for df in self:
            df.sample = sample

    def generateMask(self,maskingFunction = DataFile.maskFunction, **pars):
        """Generate mask to applied to data in data file
        
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

            - twoThetaBins (list): Bins into which 2theta is to be binned (default min(2theta),max(2theta) in steps of 0.5)

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
            if len(self.twoTheta.shape) == 3: # shape is (df,z,twoTheta), needs to be passed as (df,n,z,twoTheta)
                twoTheta = self.twoTheta[:,np.newaxis].repeat(self.counts.shape[1],axis=1) # n = scan steps
            else:
                twoTheta = self.twoTheta

        if twoThetaBins is None:
            anglesMin = np.min(twoTheta)
            anglesMax = np.max(twoTheta)
            dTheta = 0.5
            twoThetaBins = np.arange(anglesMin-0.5*dTheta,anglesMax+0.51*dTheta,dTheta)

        if self.type.lower() == 'singlecrystal':
            monitorRepeated = np.array([np.ones_like(df.counts)*df.monitor.reshape(-1,1,1) for df in self])
        else:
            monitorRepeated = np.repeat(np.repeat(self.monitor[:,np.newaxis,np.newaxis],self.counts.shape[-2],axis=1),self.counts.shape[-1],axis=2)
            monitorRepeated.shape = self.counts.shape

        summedRawIntensity, _ = np.histogram(twoTheta[np.logical_not(self.mask)],bins=twoThetaBins,weights=self.counts[np.logical_not(self.mask)])

        if applyNormalization:
            summedMonitor, _ = np.histogram(twoTheta[np.logical_not(self.mask)],bins=twoThetaBins,weights=monitorRepeated[np.logical_not(self.mask)]*self.normalization[np.logical_not(self.mask)])
        else:
            summedMonitor, _ = np.histogram(twoTheta[np.logical_not(self.mask)],bins=twoThetaBins,weights=monitorRepeated[np.logical_not(self.mask)])

        inserted, _  = np.histogram(twoTheta[np.logical_not(self.mask)],bins=twoThetaBins)
        
        normalizedIntensity = summedRawIntensity/summedMonitor
        normalizedIntensityError =  np.sqrt(summedRawIntensity)/summedMonitor

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

            - summedMonitor

        """
        
        
        twoThetaBins, normalizedIntensity, normalizedIntensityError,summedMonitor = self.sumDetector(twoThetaBins=twoThetaBins,applyNormalization=applyNormalization,\
                                                                                       correctedTwoTheta=correctedTwoTheta)

        TwoThetaPositions = 0.5*(twoThetaBins[:-1]+twoThetaBins[1:])

        if not 'fmt' in kwargs:
            kwargs['fmt'] = '-'

        if ax is None:
            fig,ax = plt.subplots()

        ax._errorbar = ax.errorbar(TwoThetaPositions,normalizedIntensity,yerr=normalizedIntensityError,**kwargs)
        ax.set_xlabel(r'$2\theta$ [deg]')
        ax.set_ylabel(r'Intensity [arb]')

        def format_coord(ax,xdata,ydata):
            if not hasattr(ax,'xfmt'):
                ax.mean_x_power = _tools.roundPower(np.mean(np.diff(ax._errorbar.get_children()[0].get_data()[0])))
                ax.xfmt = r'$2\theta$ = {:3.'+str(ax.mean_x_power)+'f} Deg'
            if not hasattr(ax,'yfmt'):
                ymin,ymax,ystep = [f(ax._errorbar.get_children()[0].get_data()[1]) for f in [np.min,np.max,len]]
                
                ax.mean_y_power = _tools.roundPower((ymax-ymin)/ystep)
                ax.yfmt = r'Int = {:.'+str(ax.mean_y_power)+'f} cts'

            return ', '.join([ax.xfmt.format(xdata),ax.yfmt.format(ydata)])

        ax.format_coord = lambda format_xdata,format_ydata:format_coord(ax,format_xdata,format_ydata)

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

        if self.type.lower() in ['singlecrystal','powder']:
            shape = self.counts.shape
            
            intensityMatrix = np.divide(self.counts,self.normalization*self.monitor[:,:,np.newaxis,np.newaxis]).reshape(-1,shape[2],shape[3])
            mask = self.mask.reshape(-1,shape[2],shape[3])
            ax.titles = np.concatenate([[df.fileName]*len(df.A3) for df in self],axis=0)
        else:
            # Find intensity
            intensityMatrix = np.divide(self.counts,self.normalization*self.monitor[:,np.newaxis,np.newaxis])
            mask = self.mask
            

        if masking is True: # If masking, apply self.mask
            intensityMatrix[np.logical_not(mask)] = np.nan

        # Find plotting limits (For 2D pixel limits found later)
        thetaLimits = [f(twoTheta) for f in [np.min,np.max]]
        intLimits = [f(intensityMatrix) for f in [np.nanmin,np.nanmax]]

        # Copy relevant data to the axis
        ax.intensityMatrix = intensityMatrix
        ax.intLimits = intLimits
        ax.twoTheta = twoTheta
        ax.twoThetaLimits = thetaLimits
        

        if not hasattr(kwargs,'fmt'):
            kwargs['fmt']='-'

        if self.type.upper() == 'OLD DATA': # Data is 1D, plot using errorbar
            ax.titles = [df.fileName for df in self]
            # calculate errorbars
            if 'colorbar' in kwargs: # Cannot be used for 1D plotting....
                del kwargs['colorbar']
            ax.errorbarMatrix = np.divide(np.sqrt(self.counts),self.normalization*self.monitor[:,np.newaxis,np.newaxis])
            def plotSpectrum(ax,index=0,kwargs=kwargs):
                if kwargs is None:
                    kwargs = {}
                if hasattr(ax,'_errorbar'): # am errorbar has already been plotted, delete ot
                    ax._errorbar.remove()
                    del ax._errorbar
                
                if hasattr(ax,'color'): # use the color from previous plot
                    kwargs['color']=ax.color
                
                if hasattr(ax,'fmt'):
                    kwargs['fmt']=ax.fmt

                # Plot data
                ax._errorbar = ax.errorbar(ax.twoTheta[index],ax.intensityMatrix[index],yerr=ax.errorbarMatrix[index].flatten(),**kwargs)
                ax.fmt = kwargs['fmt']
                ax.index = index # Update index and color
                ax.color = ax._errorbar.lines[0].get_color()
                # Set plotting limits and title
                ax.set_xlim(*ax.twoThetaLimits)
                ax.set_ylim(*ax.intLimits)
                ax.set_title(ax.titles[index])
                plt.draw()

                ax.set_ylabel('Inensity [arb]')
            
        elif self.type.upper() == 'POWDER':
            ax.titles = [df.fileName for df in self]
            # Find limits for y direction
            
            ax.twoTheta = np.array([df.twoTheta for df in self])
            ax.idxSpans = np.cumsum([len(df.A3) for df in self]) # limits of indices corresponding to data file limits
            ax.IDX = -1 # index of current data file
            ax.twoThetaLimits = [f(ax.twoTheta) for f in [np.nanmin,np.nanmax]]
            ax.pixelLimits = [-0.1,0.1]

            def plotSpectrum(ax,index=0,kwargs=kwargs):
                # find color bar limits
                vmin,vmax = ax.intLimits

                newIDX = np.sum(index>=ax.idxSpans)
                if newIDX != ax.IDX:
                    ax.IDX = newIDX
                    if hasattr(ax,'_pcolormesh'):
                        ax.cla()
                    ax._pcolormesh = ax.pcolormesh(self.twoTheta[ax.IDX],self.pixelPosition[ax.IDX,2],ax.intensityMatrix[index],shading='auto',vmin=vmin,vmax=vmax)
                
                elif hasattr(ax,'_pcolormesh'):
                    ax._pcolormesh.set_array(ax.intensityMatrix[index])
                else:
                    ax._pcolormesh = ax.pcolormesh(self.twoTheta[ax.IDX],self.pixelPosition[ax.IDX,2],ax.intensityMatrix[index],shading='auto',vmin=vmin,vmax=vmax)

                ax.index = index
                if 'colorbar' in kwargs: # If colorbar attribute is given, use it
                    if kwargs['colorbar']: 
                        if not hasattr(ax,'_colorbar'): # If no colorbar is present, create one
                            ax._colorbar = fig.colorbar(ax._pcolormesh,ax=ax)
                # Set limits
                ax.set_xlim(*ax.twoThetaLimits)
                ax.set_ylim(*ax.pixelLimits)
                ax.set_title(ax.titles[index])
                ax.set_aspect('auto')
                
                plt.draw()
                
                ax.set_ylabel('Intensity [arb]')

        elif self.type.lower() == 'A3':
            
            
            ax.A3 = np.concatenate([df.A3 for df in self],axis=0)
            ax.twoTheta = np.array([df.twoTheta for df in self])
            ax.idxSpans = np.cumsum([len(df.A3) for df in self]) # limits of indices corresponding to data file limits
            ax.IDX = -1 # index of current data file
            ax.twoThetaLimits = [f(ax.twoTheta) for f in [np.nanmin,np.nanmax]]
            ax.pixelLimits = [-0.1,0.1]

            def plotSpectrum(ax,index=0,kwargs=kwargs):
                # find color bar limits
                vmin,vmax = ax.intLimits

                newIDX = np.sum(index>=ax.idxSpans)
                if newIDX != ax.IDX:
                    ax.IDX = newIDX
                    if hasattr(ax,'_pcolormesh'):
                        ax.cla()
                    ax._pcolormesh = ax.pcolormesh(self.twoTheta[ax.IDX],self.pixelPosition[ax.IDX,2],ax.intensityMatrix[index],shading='auto',vmin=vmin,vmax=vmax)
                
                elif hasattr(ax,'_pcolormesh'):
                    ax._pcolormesh.set_array(ax.intensityMatrix[index])
                else:
                    ax._pcolormesh = ax.pcolormesh(self.twoTheta[ax.IDX],self.pixelPosition[ax.IDX,2],ax.intensityMatrix[index],shading='auto',vmin=vmin,vmax=vmax)

                
                ax.index = index
                if 'colorbar' in kwargs: # If colorbar attribute is given, use it
                    if kwargs['colorbar']: 
                        if not hasattr(ax,'_colorbar'): # If no colorbar is present, create one
                            ax._colorbar = fig.colorbar(ax._imshow,ax=ax)
                # Set limits
                ax.set_xlim(*ax.twoThetaLimits)
                ax.set_ylim(*ax.pixelLimits)
                #print(index)
                ax.set_title(ax.titles[index]+' - A3: {:.2f} [deg]'.format(ax.A3[index]))
                ax.set_aspect('auto')
                
                
                plt.draw()

            
            ax.set_ylabel(r'Pixel z position [m]')

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
        def onKeyPress(self,event): # pragma: no cover
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
            elif event.key in ['pageup']: # Pressing page up or page down performs steps of 10
                increaseAxis(self,step=10)
            elif event.key in ['pagedown']:
                decreaseAxis(self,step=10)

        # Call function for scrolling with mouse wheel
        def onScroll(self,event): # pragma: no cover
            if(event.button=='up'):
                increaseAxis(self)
            elif event.button=='down':
                decreaseAxis(self)
        # Connect function calls to slots
        fig.canvas.mpl_connect('key_press_event',lambda event: onKeyPress(ax,event) )
        fig.canvas.mpl_connect('scroll_event',lambda event: onScroll(ax,event) )
        
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

        fig,Ax = plt.subplots(2,1,figsize=(11,9),sharex=True)

        Ax = Ax.flatten()


        if not 'fmt' in kwargs:
            kwargs['fmt']='_'

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

    def Viewer3D(self,dqx,dqy,dqz,rlu=False,axis=2, raw=False,  log=False, grid = True, outputFunction=print, 
                 cmap='viridis'):

        """Generate a 3D view of all data files in the DatSet.
        
        Args:
        
            - dqx (float): Bin size along first axis in 1/AA
        
            - dqy (float): Bin size along second axis in 1/AA
        
            - dqz (float): Bin size along third axis in 1/AA

        Kwargs:

            - rlu (bool): Plot using reciprocal lattice units (default False)

            - axis (int): Initial view direction for the viewer (default 2)

            - raw (bool): If True plot counts else plot normalized counts (default False)

            - log (bool): Plot intensity as logarithm of intensity (default False)

            - grid (bool): Plot a grid on the figure (default True)

            - outputFunction (function): Function called when clicking on the figure (default print)

            - cmap (str): Name of color map used for plot (default viridis)
        
        """
        if rlu:
            #raise NotImplementedError('Currently, only plotting using Q space is supported.')
            pos = np.array(np.concatenate([np.einsum('ij,jk',df.UBInv,df.q.reshape(3,-1)) for df in self],axis=-1))

        else:
            pos = np.array(np.concatenate([df.q.reshape(3,-1) for df in self],axis=-1))

        if not raw:
            data = np.concatenate([df.intensity.flatten()  for df in self])
        else:
            data = np.concatenate([df.counts.flatten()  for df in self])
        Data,bins = _tools.binData3D(dqx,dqy,dqz,pos=pos,data=data)

        return Viewer3D.Viewer3D(Data,bins,axis=axis, grid=grid, log=log, outputFunction=outputFunction, cmap=cmap)



    def export_PSI_format(self,dTheta=0.2,twoThetaOffset=0,bins=None,outFile=None,applyNormalization=True,correctedTwoTheta=True,sampleName=True,temperature=True,magneticField=False,electricField=False,fileNumber=True):

        """
        The function takes a data set and merge the files.
        Outputs a .dat file in PSI format (Fullprof inst. 8)
        Saves the file with input name
        Data files used in the export is given in output file
        
        Kwargs:
            
            - dTheta (Float): stepsize of binning if no nins is given (default is 0.2)
            
            - twoThetaOffset (float): Linear shift of two theta, default is 0. To be used if a4 in hdf file is incorrect
            
            - Bins (list): Bins into which 2theta is to be binned (default min(2theta),max(2theta) in steps of 0.2)
            
            - outFile (str): String that will be used for outputfile. Default is automatic generated name.
            
        - Arguments for automatic file name:
                
            - sampleName (bool): Include sample name in filename. Default is True.
        
            - temperature (bool): Include temperature in filename. Default is True.
        
            - magneticField (bool): Include magnetic field in filename. Default is False.
        
            - electricField (bool): Include electric field in filename. Default is False.
        
            - fileNumber (bool): Include sample number in filename. Default is True.
            
        Kwargs for sumDetector:

            - twoThetaBins (array): Actual bins used for binning (default [min(twoTheta)-dTheta/2,max(twoTheta)+dTheta/2] in steps of dTheta=0.2 Deg)
                
            - applyNormalization (bool): Use normalization files (default True)
                
            - correctedTwoTheta (bool): Use corrected two theta for 2D data (default true)
            
        Returns:
            
            .dat file in PSI format with input name
            
        Note: Input is a data set.
            
        Example:
            >>> inputNumber = _tools.fileListGenerator(565,folder)
            >>> ds = DataSet.DataSet(inputNumber)
            >>> for df in ds:
            ...    if np.any(np.isnan(df.monitor)) or np.any(np.isclose(df.monitor,0.0)):
            ...        df.monitor = np.ones_like(df.monitor)
            >>> export_PSI_format(ds)
        
        """

        twoTheta = self.twoTheta
        
        anglesMin = np.min(twoTheta)
        anglesMax = np.max(twoTheta)
        
        if bins is None:
            bins = np.arange(anglesMin-0.5*dTheta,anglesMax+0.51*dTheta,dTheta)
        
        bins,intensity,err,monitor = self.sumDetector(bins,applyNormalization=applyNormalization,correctedTwoTheta=correctedTwoTheta)
        
        bins = bins + twoThetaOffset
        
        # find mean monitor
        meanMonitor = np.median(monitor)
        intensity[np.isnan(intensity)] = -1
        
        # rescale intensity and err
        intensity*=meanMonitor
        err*=meanMonitor
        
        step = np.mean(np.diff(bins))
        start = bins[0]+0.5*step
        stop = bins[-1]-0.5*step
        
        temperatures = [df.temperature for df in self]
        meanTemp = np.mean(temperatures)
        stdTemp = np.std(temperatures)

        if np.all([x == self.sample[0].name for x in [s.name for s in self.sample[1:]]]):
            samName = self.sample[0].name        #.decode("utf-8")
        else:
            samName ='Unknown! Combined different sample names'
        
        if np.all([np.isclose(x,self.waveLength[0]) for x in self.waveLength[1:]]):
            waveLength = self.waveLength[0]
        else:
            waveLength ='Unknown! Combined different Wavelengths'
        

        # reshape intensity and err to fit into (10,x)
        intNum = len(intensity)
        
        # How many empty values to add to allow reshape
        addEmpty = int(10*np.ceil(intNum/10.0)-intNum)
        
        intensity = np.concatenate([intensity,addEmpty*[np.nan]]).reshape(-1,10)
        err = np.concatenate([err,addEmpty*[np.nan]]).reshape(-1,10)
        
        ## Generate output to DMC file format
        titleLine = "DMC, "+samName
        paramLine = "lambda={:9.5f}, T={:8.3f}, dT={:7.3f}, Date='{}'".format(waveLength,meanTemp,stdTemp,self[0].startTime)#.decode("utf-8"))
        paramLine2= ' '+' '.join(["{:7.3f}".format(x) for x in [start,step,stop]])+" {:7.0f}".format(meanMonitor)+'., sample="'+samName+'"'
        
        dataLinesInt = '\n'.join([' '+' '.join(["{:6.0f}.".format(x).replace('nan.','    ') for x in line]) for line in intensity])
        dataLinesErr = '\n'.join([' '+' '.join(["{:7.1f}".format(x).replace('nan.','    ') for x in line]) for line in err])
        
        ## Generate bottom information part
        if len(self) == 1:
            year = 2022
            fileNumbers = str(int(self.fileName[0].split('n')[-1].split('.')[0]))
        else:
            year,fileNumbers = _tools.numberStringGenerator(self.fileName)
        
        fileList = " Filelist='dmc:{}:{}'".format(year,fileNumbers)
        
        minmax = [np.nanmin,np.nanmax]
        
        twoThetaStart = self.twoTheta[:,0]
        twoTheta = [np.min(twoThetaStart),np.max(twoThetaStart)]
        Counts = [int(func(intensity)) for func in minmax]
        numor = fileNumbers.replace('-',' ')
        Npkt = len(bins) - 1        
        
        owner = self[-1].user#.decode("utf-8")
        a1 = self[-1].monochromatorRotationAngle[0]
        a2 = self[-1].monochromatorTakeoffAngle[0]
        a3 = self[-1].A3[0]
        mcv = self[-1].monochromatorCurvature[0]
        mtx = self[-1].monochromatorTranslationLower[0]
        mty = self[-1].monochromatorTranslationUpper[0]
        mgu = self[-1].monochromatorGoniometerUpper[0]
        mgl = self[-1].monochromatorGoniometerLower[0]
        
        bMon = [df.protonBeam for df in self]
        pMon = [df.monitor for df in self]
        sMon = [[0.0]]
        
        timeMin, timeMax = [func(self.time) for func in minmax]
        sMonMin, sMonMax = [func(sMon) for func in minmax]
        bMonMin, bMonMax = [func(bMon) for func in minmax]
        aMon = np.mean([0.0 for df in self])
        pMonMin, pMonMax = [func(pMon) for func in minmax]
        muR = 0.0                           #self[-1].sample.sample_mur[0]
        preset = self[-1].mode      #.decode("utf-8")
        
        paramLines = []
        paramLines.append(" a4={:1.1f}. {:1.1f}.; Counts={} {}; Numor={}; Npkt={}; owner='{}'".format(*twoTheta,*Counts,numor,Npkt,owner))
        paramLines.append('  a1={:4.2f}; a2={:3.2f}; a3={:3.2f}; mcv={:3.2f}; mtx={:3.2f}; mty={:3.2f}; mgu={:4.3f}; mgl={:4.3f}; '.format(a1,a2,a3,mcv,mtx,mty,mgu,mgl))
        paramLines.append('  time={:4.4f} {:4.4f}; sMon={:4.0f}. {:4.0f}.; bMon={:3.0f}. {:3.0f}.; aMon={:1.0f}'.format(timeMin,timeMax,sMonMin,sMonMax,bMonMin,bMonMax,aMon))
        paramLines.append("  pMon={:7.0f}. {:7.0f}.; muR={:1.0f}.; Preset='{}'".format(float(pMonMin),float(pMonMax),muR,preset))
        paramLines.append("  calibration='{}'".format(self[-1].normalizationFile))
        paramLines.append("")
        fileString = '\n'.join([titleLine,paramLine,paramLine2,dataLinesInt,dataLinesErr,fileList,*paramLines])
        
        # get magnetic field
        # get electric field
        mag = "not defined"
        elec = "not defined"
        
        if outFile is None:
            saveFile = "DMC"
            if sampleName == True:
                saveFile += f"_{samName[:6]}"
            if temperature == True:
                saveFile += "_" + str(meanTemp).replace(".","p")[:3] + "K"
            if magneticField == True:
                saveFile += "_" + mag + "T"
            if electricField == True:
                saveFile += "_" + elec + "keV"
            if fileNumber == True:
                saveFile += "_" + fileNumbers.replace(',','_')  
        else:
            saveFile = str(outFile.replace('.dat',''))
            
        with open(saveFile+".dat",'w') as sf:
            sf.write(fileString)

    def export_xye_format(self,dTheta=0.2,twoThetaOffset=0,bins=None,outFile=None,applyNormalization=True,correctedTwoTheta=True,sampleName=True,temperature=True,magneticField=False,electricField=False,fileNumber=True):

        """
        The function takes a data set and merge the files.
        Outputs a .xye file in with a comment line with info and xye data
        Saves the file with input name
        
        Kwargs:
            
            - dTheta (Float): stepsize of binning if no nins is given (default is 0.2)
            
            - twoThetaOffset (float): Linear shift of two theta, default is 0. To be used if a4 in hdf file is incorrect
            
            - Bins (list): Bins into which 2theta is to be binned (default min(2theta),max(2theta) in steps of 0.2)
            
            - outFile (str): String that will be used for outputfile. Default is automatic generated name.
            
        - Arguments for automatic file name:
                
            - sampleName (bool): Include sample name in filename. Default is True.
        
            - temperature (bool): Include temperature in filename. Default is True.
        
            - magneticField (bool): Include magnetic field in filename. Default is False.
        
            - electricField (bool): Include electric field in filename. Default is False.
        
            - fileNumber (bool): Include sample number in filename. Default is True.
            
        Kwargs for sumDetector:

            - twoThetaBins (array): Actual bins used for binning (default [min(twoTheta)-dTheta/2,max(twoTheta)+dTheta/2] in steps of dTheta=0.2 Deg)
                
            - applyNormalization (bool): Use normalization files (default True)
                
            - correctedTwoTheta (bool): Use corrected two theta for 2D data (default true)
            
        Returns:
            
            .xye file in with a comment line with info and xye data
        
        Note: Input is a data set.
            
        Example:
            >>> inputNumber = _tools.fileListGenerator(565,folder)
            >>> ds = DataSet.DataSet(inputNumber)
            >>> for df in ds:
            ...    if np.any(np.isnan(df.monitor)) or np.any(np.isclose(df.monitor,0.0)):
            ...        df.monitor = np.ones_like(df.monitor)
            >>> export_xye_format(ds)
            
        """

        twoTheta = self.twoTheta
        
        anglesMin = np.min(twoTheta)
        anglesMax = np.max(twoTheta)
        
        if bins is None:
            bins = np.arange(anglesMin-0.5*dTheta,anglesMax+0.51*dTheta,dTheta)
        
        bins,intensity,err,monitor = self.sumDetector(bins,applyNormalization=applyNormalization,correctedTwoTheta=correctedTwoTheta)
        
        bins = bins + twoThetaOffset
        
        # find mean monitor
        meanMonitor = np.median(monitor)
        intensity[np.isnan(intensity)] = -1
        
        # rescale intensity and err
        intensity*=meanMonitor
        err*=meanMonitor
        
        step = np.mean(np.diff(bins))
        start = np.min(bins)+0.5*step
        stop = np.max(bins)-0.5*step
        
        Centres=0.5*(bins[1:]+bins[:-1])
        saveData = np.array([Centres,intensity,err])
        
        if np.all([x == self.sample[0].name for x in [s.name for s in self.sample[1:]]]):
            samName = self.sample[0].name        #.decode("utf-8")
        else:
            samName ='Unknown! Combined different sample names'

        if np.all([np.isclose(x,self.waveLength[0]) for x in self.waveLength[1:]]):
            waveLength = self.waveLength[0]
        else:
            waveLength ='Unknown! Combined different Wavelengths'
        
        temperatures = np.array([df.temperature for df in self])
        meanTemp = np.mean(temperatures)
        
        # fileNumbers = str(self.fileName) 
        # fileNumbers_short = str(int(self.fileName[0].split('n')[-1].split('.')[0]))  # 
        
        if len(self) == 1:
            year = 2022
            fileNumbers = str(int(self.fileName[0].split('n')[-1].split('.')[0]))
        else:
            year,fileNumbers = _tools.numberStringGenerator(self.fileName)
        
        titleLine1 = f"# DMC at SINQ, PSI: Sample name = {samName}, wavelength = {str(waveLength)[:5]} AA, T = {str(meanTemp)[:5]} K"
        titleLine2 = "# Filelist='dmc:{}:{}'".format(year,fileNumbers)
        titleLine3= '# '+' '.join(["{:7.3f}".format(x) for x in [start,step,stop]])+" {:7.0f}".format(meanMonitor)+'., sample="'+samName+'"'

            
        # get magnetic field
        # get electric field
        mag = "not defined"
        elec = "not defined"
        
        if outFile is None:
            saveFile = "DMC"
            if sampleName == True:
                saveFile += f"_{samName[:6]}"
            if temperature == True:
                saveFile += "_" + str(meanTemp).replace(".","p")[:3] + "K"
            if magneticField == True:
                saveFile += "_" + mag + "T"
            if electricField == True:
                saveFile += "_" + elec + "keV"
            if fileNumber == True:
                saveFile += "_" + fileNumbers.replace(',','_') 
        else:
            saveFile = str(outFile.replace('.xye',''))
            
        with open(saveFile+".xye",'w') as sf:
            sf.write(titleLine1+"\n")    
            sf.write(titleLine2+"\n") 
            sf.write(titleLine3+"\n") 
            np.savetxt(sf,saveData.T,delimiter='  ')
            sf.close()
        


            
    
            
            
def add(*listinput,PSI=True,xye=True,folder=None,dTheta=0.2,twoThetaOffset=0,bins=None,outFile=None,applyNormalization=True,correctedTwoTheta=True,sampleName=True,temperature=True,magneticField=False,electricField=False,fileNumber=True):

    """
    
    Takes a set/series file numbers and export a added/merged file. 
    The input is read as a tuple and can be formatted as int, str, list, and several arguments separated by comma can be given. 
    If one argument is a list or str, multiple filenumbers can be given inside.
    
    Exports PSI and xye format file for all scans. 
    
    Kwargs:
        
        - listinput (tuple): The function will add/merge all elements of the tuple/list. Files can be given as int, str, list.
        
        - folder (str): Path to directory for data files, default is current working directory
        
        - outFile (str): string for name of outfile (given without extension)
        
        - PSI (bool): Export PSI format. Default is True
        
        - xye (bool): Export xye format. Default is True
        
    - Arguments for automatic file name:
            
        - sampleName (bool): Include sample name in filename. Default is True.
    
        - temperature (bool): Include temperature in filename. Default is True.
    
        - magneticField (bool): Include magnetic field in filename. Default is False.
    
        - electricField (bool): Include electric field in filename. Default is False.
    
        - fileNumber (bool): Include sample number in filename. Default is True.
        
    Kwargs for sumDetector:

        - twoThetaBins (array): Actual bins used for binning (default [min(twoTheta)-dTheta/2,max(twoTheta)+dTheta/2] in steps of dTheta=0.2 Deg)
            
        - applyNormalization (bool): Use normalization files (default True)
            
        - correctedTwoTheta (bool): Use corrected two theta for 2D data (default true)
        
    Example:    
        >>> add(565,566,567,(570),'571-573',[574],sampleName=False,temperature=False)
        
        output:
            DMC_565-567_570-574 as both .dat and xye files
    """    

    if folder is None:
        folder = os.getcwd()
        
    listOfDataFiles = str()
    
    if type(listinput) == tuple:
        for elemnt in listinput:
            elemnt = str(elemnt)
            elemnt = elemnt.replace('"','').replace("'","").replace('(','').replace(')','').replace('[','').replace(']','').strip(',')
            listOfDataFiles += f"{elemnt},"
        print(f"Export of added files: {listOfDataFiles[:-1]}")
        inputNumber = _tools.fileListGenerator(listOfDataFiles[:-1],folder)
        print(inputNumber)
        ds = DataSet(inputNumber)
        for df in ds:
            if np.any(np.isnan(df.monitor)) or np.any(np.isclose(df.monitor,0.0)):
                df.monitor = np.ones_like(df.monitor)
            print('I got ehre 2')
        if PSI == True:
            ds.export_PSI_format(dTheta,twoThetaOffset,bins,outFile,applyNormalization,correctedTwoTheta,sampleName,temperature,magneticField,electricField,fileNumber)    
        if xye == True:
            ds.export_xye_format(dTheta,twoThetaOffset,bins,outFile,applyNormalization,correctedTwoTheta,sampleName,temperature,magneticField,electricField,fileNumber)      
    else:
        print("Cannot export! Something wrong with input")       


# add(565,566,567,(570),'571-573',[574],sampleName=False,temperature=False)



        
def export(*listinput,PSI=True,xye=True,folder=None,dTheta=0.2,twoThetaOffset=0,bins=None,outFile=None,applyNormalization=True,correctedTwoTheta=True,sampleName=True,temperature=True,magneticField=False,electricField=False,fileNumber=True):

    """
    
    Takes a set file numbers and export induvidually. 
    The input is read as a tuple and can be formatted as int, str, list, and arguments separated by comma is export induvidually. 
    If one argument is a list or str, multiple filenumbers can be given inside, and they will be added/merged.
    
    Exports PSI and xye format file for all scans. 
    
    Kwargs:
        
        - listinput (tuple): the function will export all elements of the tuple/list inducidually. Files can be merged by [], '', and () notation.
        
        - folder (str): Path to directory for data files, default is current working directory
        
        - PSI (bool): Export PSI format. Default is True
        
        - xye (bool): Export xye format. Default is True
        
        - outFile (str): string for name of outfile (given without extension)
        
    - Arguments for automatic file name:
            
        - sampleName (bool): Include sample name in filename. Default is True.
    
        - temperature (bool): Include temperature in filename. Default is True.
    
        - magneticField (bool): Include magnetic field in filename. Default is False.
    
        - electricField (bool): Include electric field in filename. Default is False.
    
        - fileNumber (bool): Include sample number in filename. Default is True.
        
    Kwargs for sumDetector:

        - twoThetaBins (array): Actual bins used for binning (default [min(twoTheta)-dTheta/2,max(twoTheta)+dTheta/2] in steps of dTheta=0.2 Deg)
            
        - applyNormalization (bool): Use normalization files (default True)
            
        - correctedTwoTheta (bool): Use corrected two theta for 2D data (default true)
        
    Example:    
        >>> export(565,'566',[567,568,570,571],'570-573',(574,575),sampleName=None,temperature=False)  
        
        output: DMC_565, DMC_566, DMC_567_568_570_571, DMC_570-573, DMC_574-575 as both .dat and xye files
        
    """    

    if folder is None:
        folder = os.getcwd()
    
    if type(listinput) == tuple:
        for elemnt in listinput:
            elemnt = str(elemnt)
            elemnt = elemnt.replace('"','').replace("'","").replace('(','').replace(')','').replace('[','').replace(']','').strip(',')
            print(f"Export of: {elemnt}")
            inputNumber = _tools.fileListGenerator(elemnt,folder)
            try:
                ds = DataSet(inputNumber)
                for df in ds:
                    if np.any(np.isnan(df.monitor)) or np.any(np.isclose(df.monitor,0.0)):
                        df.monitor = np.ones_like(df.monitor)
                if PSI == True:
                    ds.export_PSI_format(dTheta,twoThetaOffset,bins,outFile,applyNormalization,correctedTwoTheta,sampleName,temperature,magneticField,electricField,fileNumber)    
                if xye == True:
                    ds.export_xye_format(dTheta,twoThetaOffset,bins,outFile,applyNormalization,correctedTwoTheta,sampleName,temperature,magneticField,electricField,fileNumber)      
            except:
                print(f"Cannot export! File is wrong format: {elemnt}")
    else:
        print("Cannot export! Something wrong with input")
        

# export(565,'566',[567,568,570,571],'570-573',(574,575),sampleName=False,temperature=False)  
        




def export_from(startFile,PSI=True,xye=True,folder=None,dTheta=0.2,twoThetaOffset=0,bins=None,outFile=None,applyNormalization=True,correctedTwoTheta=True,sampleName=True,temperature=True,magneticField=False,electricField=False,fileNumber=True):
    
    """
    
    Takes a starting file number and export xye format file for all the following files in the folder.

    Exports PSI and xye format file for all scans. 
    
    Kwargs:
        
        - startFile (int): First file number for export
        
        - folder (str): Path to directory for data files, default is current working directory
        
        - PSI (bool): Export PSI format. Default is True
        
        - xye (bool): Export xye format. Default is True
        
        - all from export_PSI_format and export_xye_format
        
    - Arguments for automatic file name:
            
        - sampleName (bool): Include sample name in filename. Default is True.
    
        - temperature (bool): Include temperature in filename. Default is True.
    
        - magneticField (bool): Include magnetic field in filename. Default is False.
    
        - electricField (bool): Include electric field in filename. Default is False.
    
        - fileNumber (bool): Include sample number in filename. Default is True.
        
    Kwargs for sumDetector:

        - twoThetaBins (array): Actual bins used for binning (default [min(twoTheta)-dTheta/2,max(twoTheta)+dTheta/2] in steps of dTheta=0.2 Deg)
            
        - applyNormalization (bool): Use normalization files (default True)
            
        - correctedTwoTheta (bool): Use corrected two theta for 2D data (default true)
        
    Example:       
        >>> export_from(590,sampleName=False,temperature=False)    
        
    """
    if folder is None:
        folder = os.getcwd()
    
    hdf_files = [f for f in os.listdir(folder) if f.endswith('.hdf')]
    last_hdf = hdf_files[-1]

    numberOfFiles = int(last_hdf.strip('.hdf').split('n')[-1]) - int(startFile)
    
    fileList = list(range(startFile,startFile+numberOfFiles))
    
    for file in fileList:  

        file = str(file)
        file = file.replace('"','').replace("'","").replace('(','').replace(')','').replace('[','').replace(']','').replace(' ','').strip(',')
        print(f"Export of: {file}")
        try:
            inputNumber = _tools.fileListGenerator(file,folder)
            ds = DataSet(inputNumber)
            for df in ds:
                if np.any(np.isnan(df.monitor)) or np.any(np.isclose(df.monitor,0.0)):
                    df.monitor = np.ones_like(df.monitor)
            if PSI == True:
                ds.export_PSI_format(dTheta,twoThetaOffset,bins,outFile,applyNormalization,correctedTwoTheta,sampleName,temperature,magneticField,electricField,fileNumber)    
            if xye == True:
                ds.export_xye_format(dTheta,twoThetaOffset,bins,outFile,applyNormalization,correctedTwoTheta,sampleName,temperature,magneticField,electricField,fileNumber)      
        except:
            print(f"Cannot export! File is wrong format: {file}")
            
# export_from(587,sampleName=False,temperature=False)    





def export_from_to(startFile,endFile,PSI=True,xye=True,folder=None,dTheta=0.2,twoThetaOffset=0,bins=None,outFile=None,applyNormalization=True,correctedTwoTheta=True,sampleName=True,temperature=True,magneticField=False,electricField=False,fileNumber=True):

    """
    
    Takes a starting file number and a end file number, export for all scans between (including start and end)

    Exports PSI and xye format file for all scans. 
    
    Kwargs:
        
        - startFile (int): First file number for export
        
        - endFile (int): Final file number for export
        
        - folder (str): Path to directory for data files, default is current working directory
        
        - PSI (bool): Export PSI format. Default is True
        
        - xye (bool): Export xye format. Default is True
        
        - all from export_PSI_format and export_xye_format
        
    - Arguments for automatic file name:
            
        - sampleName (bool): Include sample name in filename. Default is True.
    
        - temperature (bool): Include temperature in filename. Default is True.
    
        - magneticField (bool): Include magnetic field in filename. Default is False.
    
        - electricField (bool): Include electric field in filename. Default is False.
    
        - fileNumber (bool): Include sample number in filename. Default is True.
        
    Kwargs for sumDetector:

        - twoThetaBins (array): Actual bins used for binning (default [min(twoTheta)-dTheta/2,max(twoTheta)+dTheta/2] in steps of dTheta=0.2 Deg)
            
        - applyNormalization (bool): Use normalization files (default True)
            
        - correctedTwoTheta (bool): Use corrected two theta for 2D data (default true)
        
    Example:     
        >>> export_from_to(565,570,sampleName=False,temperature=False)
        
        output: DMC_565, DMC_566, DMC_567, DMC_568, DMC_569, DMC__570 as both .xye and .dat files
        
    """
    if folder is None:
        folder = os.getcwd()
        
    fileList = list(range(startFile,endFile+1))
    
    for file in fileList:    
        file = str(file)
        file = file.replace('"','').replace("'","").replace('(','').replace(')','').replace('[','').replace(']','').replace(' ','').strip(',')
        print(f"Export of: {file}")
        try:
            inputNumber = _tools.fileListGenerator(file,folder)
            ds = DataSet(inputNumber)
            for df in ds:
                if np.any(np.isnan(df.monitor)) or np.any(np.isclose(df.monitor,0.0)):
                    df.monitor = np.ones_like(df.monitor)
            if PSI == True:
                ds.export_PSI_format(dTheta,twoThetaOffset,bins,outFile,applyNormalization,correctedTwoTheta,sampleName,temperature,magneticField,electricField,fileNumber)    
            if xye == True:
                ds.export_xye_format(dTheta,twoThetaOffset,bins,outFile,applyNormalization,correctedTwoTheta,sampleName,temperature,magneticField,electricField,fileNumber)      
        except:
            print(f"Cannot export! File is wrong format: {file}")


# export_from_to(565,570,sampleName=False,temperature=False)







def export_list(listinput,PSI=True,xye=True,folder=None,dTheta=0.2,twoThetaOffset=0,bins=None,outFile=None,applyNormalization=True,correctedTwoTheta=True,sampleName=True,temperature=True,magneticField=False,electricField=False,fileNumber=True):

    """
    
    Takes a list and export all elements induvidually. If a list is given inside the list, these files will be added/merged.

    Exports PSI and xye format file for all scans. 
    
    Kwargs:
        
        - list input (list: List of files that will be exported.
        
        - folder (str): Path to directory for data files, default is current working directory
        
        - PSI (bool): Export PSI format. Default is True
        
        - xye (bool): Export xye format. Default is True
        
        - all from export_PSI_format and export_xye_format
        
    - Arguments for automatic file name:
            
        - sampleName (bool): Include sample name in filename. Default is True.
    
        - temperature (bool): Include temperature in filename. Default is True.
    
        - magneticField (bool): Include magnetic field in filename. Default is False.
    
        - electricField (bool): Include electric field in filename. Default is False.
    
        - fileNumber (bool): Include sample number in filename. Default is True.
        
    Kwargs for sumDetector:

        - twoThetaBins (array): Actual bins used for binning (default [min(twoTheta)-dTheta/2,max(twoTheta)+dTheta/2] in steps of dTheta=0.2 Deg)
            
        - applyNormalization (bool): Use normalization files (default True)
            
        - correctedTwoTheta (bool): Use corrected two theta for 2D data (default true)
        
    Example:    
        >>> export_list([565,566,567,[569,570]],sampleName=False,temperature=False) 
        
        output: DMC_565, DMC_566, DMC_567, DMC_569_570 as both .xye and .dat files
        
    """    

    if folder is None:
        folder = os.getcwd()
        
    for file in listinput:   
        file = str(file)
        file = file.replace('"','').replace("'","").replace('(','').replace(')','').replace('[','').replace(']','').replace(' ','').strip(',')
        print(f"Export of: {file}")           
        try:
            inputNumber = _tools.fileListGenerator(file,folder)
            ds = DataSet(inputNumber)
            for df in ds:
                if np.any(np.isnan(df.monitor)) or np.any(np.isclose(df.monitor,0.0)):
                    df.monitor = np.ones_like(df.monitor)
            if PSI == True:
                ds.export_PSI_format(dTheta,twoThetaOffset,bins,outFile,applyNormalization,correctedTwoTheta,sampleName,temperature,magneticField,electricField,fileNumber)    
            if xye == True:
                ds.export_xye_format(dTheta,twoThetaOffset,bins,outFile,applyNormalization,correctedTwoTheta,sampleName,temperature,magneticField,electricField,fileNumber)      
        except:
            print(f"Cannot export! File is wrong format: {file}")
            

# export_list([565,566,567,[569,570]],sampleName=False,temperature=False)            
                

                
def subtract_PSI(file1,file2,outFile=None,folder=None):

    """
    
    This function takes two .dat files in PSI format and export a differnce curve with correct uncertainties. 
    
    The second file is scaled after the monitor of the first file.
    
    Kwargs:
        
        - PSI (bool): Subtract PSI format. Default is True
        
        - xye (bool): Subtract xye format. Default is True
        
        - outFile (str): string for name of outfile (given without extension)
                
    Example:
        >>> subtract('DMC_565.dat','DMC_573')
    
    """

    if folder is None:
        folder = os.getcwd()
        
    with open(os.path.join(folder,file1.replace('.dat','')+'.dat'),'r') as rf:
        allinfo1 = rf.readlines()
        rf.close()

    with open(os.path.join(folder,file2.replace('.dat','')+'.dat'),'r') as rf:
        allinfo2 = rf.readlines()
        rf.close()    

    info1 = allinfo1[:3] 
    info2 = allinfo2[:3] 

    if info1[2].split(',')[0].split(',')[0] != info2[2].split(',')[0].split(',')[0]:
        return print('Not same range of files! Cannot subtract.')          
        
    infoStr1 = (info1[2].split(',')[0].strip('#').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' '))
    infoArr1 = [float(x) for x in infoStr1[1:].split(' ')]

    infoStr2 = (info2[2].split(',')[0].strip('#').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' '))
    infoArr2 = [float(x) for x in infoStr2[1:].split(' ')]
        
    monitor1 = infoArr1[3]
    monitor2 = infoArr2[3]
    monitorRatio = monitor1/monitor2    
    dataPoints = int((infoArr1[2]-infoArr1[0]) / infoArr1[1]) + 1
    subInt = []
    subErr = []
    
    dataLines = int(np.ceil(dataPoints/10)) 
    commentlines = 3
    
    for intLines in range(dataLines): 
        subIntList = []
        subErrList = []
        intline1= allinfo1[intLines+commentlines]
        intline2= allinfo2[intLines+commentlines]
        errline1= allinfo1[intLines+dataLines+commentlines]
        errline2= allinfo2[intLines+dataLines+commentlines]
        intensity1 = [float(x) for x in intline1[:-2].replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('nan','').replace('na','').split(' ') if x != '' ]  
        intensity2 = [float(x) for x in intline2[:-2].replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('nan','').replace('na','').split(' ') if x != '' ] 
        err1 = [float(x) for x in errline1[:-2].replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('nan','').replace('na','').split(' ') if x != '' ] 
        err2 = [float(x) for x in errline2[:-2].replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('nan','').replace('na','').split(' ') if x != '' ] 
        for i, j in zip(intensity1,intensity2):
            subIntList.append(i-j*monitorRatio)
        for h, k in zip(err1,err2):
            subErrList.append(np.sqrt(h**2 + monitorRatio**2 * k**2))
        subInt.append(subIntList)
        subErr.append(subErrList)
    
    titleLine = str(info1[0]).strip('\n') + ', subtracted: ' + str(info2[0])  + str(info1[1]) + str(info1[2]).strip('\n')
    dataLinesInt = '\n'.join([' '+' '.join(["{:6.0f}.".format(x) for x in line]) for line in subInt])
    dataLinesErr = '\n'.join([' '+' '.join(["{:7.1f}".format(x) for x in line]) for line in subErr])
    indexParamLines = dataLines*2 + commentlines
    paramLine1 = '\n'.join([str(line).strip('\n') for line in allinfo1[indexParamLines:]])
    paramLine2 = ' subtracted:'
    paramLine3 = str(info2[0])  + str(info1[1]) + str(info1[2]).strip('\n')
    paramLine4 = ''.join([str(line) for line in allinfo2[indexParamLines:]])
    fileString = '\n'.join([titleLine,dataLinesInt,dataLinesErr,paramLine1,paramLine2,paramLine3,paramLine4])
    
    if outFile is None:
        saveFile = file1.replace('.dat','') + '_sub_' + file2.replace('.dat','')
    else:
        saveFile = str(outFile.replace('.dat',''))

    print(f'Subtracting PSI: {file1}.dat minus {file2}.dat') 

    with open(saveFile+".dat",'w') as sf:
        sf.write(fileString)
    
    
    
# subtract_PSI('DMC_565','DMC_573')


def subtract_xye(file1,file2,outFile=None,folder=None):

    """
    
    This function takes two .xye files and export a differnce curve with correct uncertainties. 
    
    The second file is scaled after the monitor of the first file.
    
    Kwargs:
        
        - PSI (bool): Subtract PSI format. Default is True
        
        - xye (bool): Subtract xye format. Default is True
        
        - outFile (str): string for name of outfile (given without extension)    
        
    Example:
        >>> subtract('DMC_565.xye','DMC_573')
        
    """
    
    if folder is None:
        folder = os.getcwd()
        
    data1 = np.genfromtxt(os.path.join(folder,file1.replace('.xye','')+'.xye'), delimiter='  ')
    data2 = np.genfromtxt(os.path.join(folder,file2.replace('.xye','')+'.xye'), delimiter='  ')  
    
    with open(os.path.join(folder,file1.replace('.xye','')+'.xye'),'r') as rf:
        info1 = rf.readlines()[:3]
        rf.close()

    with open(os.path.join(folder,file2.replace('.xye','')+'.xye'),'r') as rf:
        info2 = rf.readlines()[:3]
        rf.close()

    if info1[2].split(',')[0].split(',')[0] != info2[2].split(',')[0].split(',')[0]:
        return print('Not same range of files! Cannot subtract.')          
        
    infoStr1 = (info1[2].split(',')[0].strip('#').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' '))
    infoArr1 = [float(x) for x in infoStr1[1:].split(' ')]

    infoStr2 = (info2[2].split(',')[0].strip('#').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' '))
    infoArr2 = [float(x) for x in infoStr2[1:].split(' ')]

    monitorRatio = infoArr1[3]/infoArr2[3]

    subInt = np.subtract(data1[:,1], np.multiply(monitorRatio,(data2[:,1])))

    intErr2 = monitorRatio * data2[:,2]
    
    subErr = 0 * data2[:,1]
    
    for i in range(len(data1[:,2])):
        subErr[i] = np.sqrt( (data1[i,2])**2 + (intErr2[i])**2 ) 
    
    saveData = np.array([data1[:,0],subInt,subErr])

    if outFile is None:
        saveFile = file1.replace('.xye','') + '_sub_' + file2.replace('.xye','')
    else:
        saveFile = str(outFile.replace('.xye',''))

    print(f'Subtracting xye: {file1}.xye minus {file2}.xye')    

    with open(saveFile+".xye",'w') as sf:
        sf.write('# ' + str(info1) + "\n")   
        sf.write("# subtracted file: \n") 
        sf.write('# ' + str(info2) + "\n") 
        np.savetxt(sf,saveData.T,delimiter='  ')
        sf.close()

        
    # subtract_xye('DMC_565','DMC_573')

def subtract(file1,file2,PSI=True,xye=True,outFile=None,folder=None):
    """

    This function takes two files and export a differnce curve with correct uncertainties. 

    The second file is scaled after the monitor of the first file.

    Kwargs:
        
        - PSI (bool): Subtract PSI format. Default is True
        
        - xye (bool): Subtract xye format. Default is True
        
        - outFile (str): string for name of outfile (given without extension)    
        
    Example:
        >>> subtract('DMC_565.xye','DMC_573')

    """


    if folder is None:
        folder = os.getcwd()

    file1 = file1.replace('.xye','').replace('.dat','')
    file2 = file2.replace('.xye','').replace('.dat','')

    if PSI == True:
        try:
            subtract_PSI(file1,file2,outFile,folder=folder)
        except:
            print('Cannot subtract PSI format files')
    if xye == True:
        try:
            subtract_xye(file1,file2,outFile,folder=folder)
        except:
            print('Cannot subtract xye format files')
        
        
#subtract('DMC_565.xye','DMC_573')

def sort_export():
    
    pass

def export_help(): 
    print(" ")
    print(" The following commands are avaliable for export of powder data in DMCpy:")
    print(" ")
    print("     export, add, export_from, export_from_to, export_list")
    print(" ")
    print(" They export both PSI and xye format by default. Can be deactivated by the arguments PSI=False and xye=False")
    print(" ")
    print('      - export: For export of induvidual sets of scan files. Files can be merged by [] or "" notation, i.e. list or strings.')
    print('      - add: TThe function adds/merge all the files given. ')
    print("      - export_from: For export of all data files in a folder after a startfile")
    print("      - export_from_to: It exports all files between and including two given files")
    print("      - export_list: Takes a list and export all the files separatly. If a list is given inside the list, the files will be merged ")
    print(" ")
    print(" Examples:  ")
    print('      >>> export(565,"566",[567,568,570,571],"570-573",(574,575),sampleName=False,temperature=False)  ')
    print("      >>> add(565,566,567,(570),'571-573',[574],sampleName=False,temperature=False) ")
    print("      >>> export_from(590,fileNumber=True)  ")
    print("      >>> export_from_to(565,570,dTheta=0.25,twoThetaOffset=2.0)")
    print("      >>> export_list([565,566,567,570],temperature=False,xye=False)")
    print("      >>> export_list([565,566,567,[568,569,570]]) # This is an example of list inside a list. 568,569,570 will be merged in this case. ")
    print('      >>> add("565,567,570-573",outFile="mergefilename")')
    print('      >>> export(565,folder=r"Path\To\Data\Folder")   #Note r"..." notation')      
    print(" ")
    print(" ")
    print(" Most important kewords and aguments:")
    print(" ")
    print("     - dTheta (float): stepsize of binning if no bins is given (default is 0.2)")
    print("     - outFile (str): String that will be used for outputfile. Default is automatic generated name.")
    print("     - twoThetaOffset (float): Linear shift of two theta, default is 0. To be used if a4 in hdf file is incorrect")
    print(" ")
    print(" Arguments for automatic file name:")
    print(" ")
    print("     - sampleName (bool): Include sample name in filename. Default is True.")
    print("     - temperature (bool): Include temperature in filename. Default is True.")
    print("     - fileNumber (bool): Include sample number in filename. Default is True.")
    print("     - magneticField (bool): Include magnetic field in filename. Default is False.")
    print("     - electricField (bool): Include electric field in filename. Default is False.")
    print(" ")
    print(" ")
    print(" There is also a subtract function for subtracting PSI format files and xye format files. ")    
    print(" The files are normalized to the onitor of the first dataset.")
    print(" Input is two existing filenames with or without extenstion. ")
    print(" PSI and xye format can be deactivated by PSI = False and xye = False")    
    print(" Alternatively can subtract_PSI or subtract_xye be used")
    print(" ")
    print("      >>> subtract('DMC_565.xye','DMC_573')")    
    print(" ")
    

