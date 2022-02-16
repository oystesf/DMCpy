import h5py as hdf
import datetime
from h5py._hl import attrs
import numpy as np
import pickle as pickle
import matplotlib.pyplot as plt
import pandas as pd
import DMCpy
import os.path
from DMCpy import InteractiveViewer
from collections import defaultdict
import warnings

import copy
from DMCpy import _tools

scanTypes = ['Old Data','Powder','A3']
class Entry:
    """Dummy class for h5py group entries"""
    def __init__(self,**kwargs):
        for item,value in kwargs:
            setattr(self,item,value)

def decode(item):
    """Test and decode item to utf8"""
    if hasattr(item,'__len__'):
        if len(item)>0:
            if hasattr(item[0],'decode'):
                item = item[0].decode('utf8')
            
                    
    return item

class h5pyReader:
    """Custom class used to traverse hdf file and extract all data
    
    This object traverses the HDF file structure and creates a dummy
    Entry object for each layer. As H5PY do not traverse links already
    visited, special care is to be taken!"""
    def __init__(self,exclude=None):
        """Initialize a reader with custom exclude
        
        Kwargs: 
            - exclude (str): Exclude this first name (default None)"""
        if exclude is None:
            self.exclude = None
        else:
            self.exclude = exclude

    def __call__(self, name, h5obj):
        """Called by the hdf5 visititmes method"""
        if name == self.exclude:
            return
        
        
        # Split names by '/' and replace - with _
        name = name.replace('-','_').split('/')
        if name[0] == self.exclude:
            name = name[1:]
        if len(name) == 0:
            return 
        
        # Reverse name order to enable the use of pop
        name = name[::-1]
        
        
        # Find correct depth in object
        obj = self
        
        while len(name) != 1: # Go through name and add entries for all missing links
            # I.e: DMC/DMC_BF3_Detector/CounterMod -> 'CounterMode', 'DMC_BF3_Detector', 'DMC'
            # add 'DMC' to obj, then 'DMC_BF3_Detector'
            currentName = name.pop()
            if not hasattr(obj,currentName):
                obj.__dict__[currentName] = Entry()
            obj = getattr(obj,currentName) # get one level down object
            
        attributeName = name[0]
        if attributeName == 'lambda':
            attributeName = 'Lambda' # lambda is a key word in python
        if hasattr(h5obj,'dtype'): 
            obj.__dict__[attributeName] = np.array(h5obj,dtype=h5obj.dtype)
        
        if not hasattr(obj,attributeName): # Add the group to the data
            obj.__dict__[attributeName] = Entry()
        
        for item,value in dict(h5obj.attrs).items():
            try:
                setattr(getattr(obj,attributeName),item,value)
            except AttributeError: # cannot add things to numpy array.... alternatively add it by using _ instead
                setattr(obj,'__'+attributeName+'_'+item,value)
            

@_tools.KwargChecker()
def maskFunction(phi,maxAngle=10.0):
    """Mask all phi angles outside plus/minus maxAngle

    Args:

        - phi (array): Numpy array of phi angles to be masked

    Kwargs:

        - maxAngle (float): Mask points greater than this or less than -maxAngle in degrees (default 10)
    """
    return np.abs(phi)>maxAngle

@_tools.KwargChecker()
def findCalibration(fileName):
    """Find detector calibration for specified file

    Args:

        - fileName (str): Name of file for which calibration is needed

    Returns:

        - calibration (array): Detector efficiency

        - calibrationName (str): Name of calibration file used

    Raises:

        - fileNotFoundError

    """

    # Extract only actual file name if path is provided    
    fileName = os.path.split(fileName)[-1]

    # Split name in 'dmcyyyynxxxxxx.hdf'
    year,fileNo = [int(x) for x in fileName[3:].replace('.hdf','').split('n')]

    calibrationDict = DMCpy.calibrationDict

    # Calibration files do not cover the wanted year
    if not year in calibrationDict.keys():
        raise FileNotFoundError('Calibration files for year {} (extracted from file name "{}") is'.format(year,fileName)+\
            ' not covered in calibration tables. Please update to newest version by invoking "pip install --upgrade DMCpy"')

    yearCalib = calibrationDict[year]
    
    limits = yearCalib['limits']
    
    # Calibration name is index of the last limit below file number
    idx = np.sum([fileNo>limits])-1
    
    idx = np.max([idx,0]) # ensure that idx is not negative
    
    # Calibration is saved in yearCalib with name of calibration file
    calibrationName = yearCalib['names'][idx]
    calibration = yearCalib[calibrationName]
    return calibration,calibrationName

class DataFile(object):
    @_tools.KwargChecker(include=['radius','data','twoThetaPosition','A3','verticalPosition','Monitor','waveLength'])
    def __init__(self, file=None,**kwargs):
        """DataFile object holding all data from a single DMC powder scan file

        Kwargs:

            - file (string or object): File path or file object (default None)

            - other kwargs will be used to overwrite values otherwise loaded from file. Following are possible to overwrite:

            - radius (float)

            - data (int shaped (n,128,1152))

            - twoThetaPosition (float shaped (1), i.e. np.array([0.0]))

            - A3 (float shaped (n))

            - verticalPosition (float shaped (128))

            - Monitor (float shaped (n))

            - waveLength (float)

        If a file path is given data is loaded into this object. If an existing DataFile object
        is provided, its data is copied into the new object.

        """

        self._debugging = False
        self.kwargs = kwargs

        if not file is None: 
            if isinstance(file,DataFile): # Copy everything from provided file
                # Copy all file settings
                self.updateProperty(file.__dict__)

            elif os.path.exists(file): # load file from disk
                self.loadFile(file)


            else:
                if not file == 'DEBUG': # If testing is activated load a dummy data file
                    raise FileNotFoundError('Provided file path "{}" not found.'.format(file))

                self._debugging = True
                self.folder = None
                self.fileName = None



    @_tools.KwargChecker()
    def loadFile(self,filePath):
        if not os.path.exists(filePath):
            raise FileNotFoundError('Provided file path "{}" not found.'.format(filePath))

        self.folder, self.fileName = os.path.split(filePath)

        # Open file in reading mode
        with hdf.File(filePath,mode='r') as f:
            bulkData = h5pyReader(exclude='entry')
            f.visititems(bulkData) 

            if 'entry/data' in f: # data1 is not included as it only contains soft links
                data1 = h5pyReader()
                f['entry/data'].visititems(data1)
                bulkData.data1 = data1

        self.updateProperty(bulkData.__dict__)

        # copy important paramters to correct position
        self.radius = self.kwargs.get('radius',0.8)
        
        if 'twoThetaPosition' in self.kwargs:
            self.twoThetaPosition = self.kwargs['twoThetaPosition']

        countShape = self.DMC.detector.data.shape
        if len(countShape) == 2:
            self.scanType = 'Powder'
            if 'data' in self.kwargs:
                self.counts = self.kwargs['data']
            
            self.counts.shape = (1,*self.counts.shape)
            
            
            self.twoTheta = np.linspace(0,132,self.counts.shape[2])
            if not np.isnan(self.twoThetaPosition[0]):
                self.twoTheta+=self.twoThetaPosition
            
            
        elif len(countShape) == 3: # We have 3D data! Assume A3 scan with shape (step,128*9,height)
            if 'data' in self.kwargs:
                self.counts = self.kwargs['data']
            
            if 'A3' in self.kwargs:
                self.sample.rotation_angle = self.kwargs['A3']

            if not len(self.A3) == countShape[0]:
                self.sample.rotation_angle = self.sample.rotation_angle[:-1]

                #raise AttributeError("Scan performed is not an A3 scan... Sorry, I can't work with this....")

            if np.diff(self.A3).mean()>0:
                self.scanType = 'A3'
            else:
                raise AttributeError('Scan is not A3!')


            self.twoThetaPosition = self.twoThetaPosition[0]
            self.twoTheta = np.linspace(0,132,self.counts.shape[2])+self.twoThetaPosition
            
            
        else:
            raise AttributeError('Data file format not understood. Size of counts is {}...'.format(self.DMC.detector.data.shape))

        
        repeats = self.counts.shape[1]
        verticalPosition = self.kwargs.get('verticalPosition',np.linspace(-0.1,0.1,repeats,endpoint=True))
        
        
        self.twoTheta, z = np.meshgrid(self.twoTheta.flatten(),verticalPosition,indexing='xy')
        

        
        self.pixelPosition = np.array([self.radius*np.cos(np.deg2rad(self.twoTheta)),
                                    -self.radius*np.sin(np.deg2rad(self.twoTheta)),
                                    z]).reshape(3,*self.counts.shape[1:])
        
        
        self.Monitor = self.kwargs.get('Monitor',self.monitor)
        self.monitor = self.monitor.monitor[0]
        if self.monitor == np.array([0]): # error mode from commissioning
            self.monitor = np.ones(self.counts.shape[0])
        
        self.alpha = np.rad2deg(np.arctan2(self.pixelPosition[2],self.radius))
        self.waveLength = self.kwargs.get('waveLength',self.DMC.monochromator.wavelength[0])
        # Above line makes an implicit call to the self.calculateQ method!
        

        self.correctedTwoTheta = 2.0*np.rad2deg(np.arcsin(self.waveLength*self.Q[0]/(4*np.pi)))[np.newaxis].repeat(self.Q.shape[0],axis=0)
        
        self.phi = np.rad2deg(np.arctan2(self.q[2],np.linalg.norm(self.q[:2],axis=0)))

        self.generateMask(maskingFunction=None)
            # Create a mask only containing False as to signify all points are allowed

        # Load calibration
        try:
            self.normalization, self.normalizationFile = findCalibration(self.fileName)
        except ValueError:
            self.normalizationFile = 'None'

        if self.normalizationFile == 'None':
            self.normalization = np.ones_like(self.counts,dtype=float)
        else:
            
            if self.scanType == "A3": # A3 scan
                self.normalization = np.repeat(self.normalization[np.newaxis],self.counts.shape[0],axis=0)
                self.normalization = self.normalization.transpose(0,2,1)
            else:
                self.normalization.shape = self.counts.shape

        if hasattr(self,'sample'):
            # If no temperature is saved in sample.sample_temperature
            if not hasattr(self.sample,'sample_temperature'):
                self.sample.sample_temperature = np.array([0.0])
            if not hasattr(self.sample,'sample_name'):
                self.sample.name = 'UNKNOWN'

        self.time = self.Monitor.time
    #else:
    #    raise NotImplementedError("Expected data file to originate from DMC...")

    @property
    def A3(self):
        return self.sample.rotation_angle

    @A3.getter
    def A3(self):
        if not hasattr(self.sample,'rotation_angle'):
            self.sample.rotation_angle = np.array([0.0]*len(self.monitor))
        return self.sample.rotation_angle
        

    @A3.setter
    def A3(self,A3):
        if A3 is None:
            self.sample.rotation_angle = np.array([0.0]*len(self.monitor))
        else:
            self.sample.rotation_angle = A3
        if hasattr(self,'ki'):
            self.calculateQ()
    
    @property
    def counts(self):
        return self.DMC.detector.data

    @counts.getter
    def counts(self):
        return self.DMC.detector.data

    @counts.setter
    def counts(self,data):
        if data is None:
            raise AttributeError('Data cannot be set to None')
        else:
            self.DMC.detector.data = data


    @property
    def twoThetaPosition(self):
        return self.DMC.detector.detector_position

    @twoThetaPosition.getter
    def twoThetaPosition(self):
        return self.DMC.detector.detector_position

    @twoThetaPosition.setter
    def twoThetaPosition(self,twoTheta):
        if twoTheta is None:
            self.DMC.detector.detector_position = np.array([0.0]*len(self.monitor))
        else:
            self.DMC.detector.detector_position = twoTheta
        self.twoTheta = np.linspace(0,132,1152) + self.DMC.detector.detector_position
        if hasattr(self,'_Ki'):
            self.calculateQ()

    @property
    def Ki(self):
        return self._Ki

    @Ki.getter
    def Ki(self):
        return self._Ki

    @Ki.setter
    def Ki(self,Ki):
        self._Ki = Ki
        self.DMC.monochromator.wavelength = np.full_like(self.DMC.monochromator.wavelength,2*np.pi/Ki)
        self.calculateQ()

    @property
    def waveLength(self):
        return self.DMC.monochromator.wavelength[0]

    @waveLength.getter
    def waveLength(self):
        return self.DMC.monochromator.wavelength[0]

    @waveLength.setter
    def waveLength(self,waveLength):
        self.DMC.monochromator.wavelength = np.full_like(self.DMC.monochromator.wavelength,waveLength)
        self._Ki = 2*np.pi/waveLength
        self.calculateQ()

    def calculateQ(self):
        """Calculate Q and qx,qy,qz using the current A3 values"""

        self.ki = np.array([self.Ki,0.0,0.0]) # along ki=2pi/lambda with x
        self.ki.shape = (3,1,1)

        self.kf = self.Ki * np.array([np.cos(np.deg2rad(self.twoTheta))*np.cos(np.deg2rad(self.alpha)),
                                    -np.sin(np.deg2rad(self.twoTheta))*np.cos(np.deg2rad(self.alpha)),
                                    np.sin(np.deg2rad(self.alpha))])
        self.q = self.ki-self.kf   
        if len(self.DMC.detector.data.shape) == 3: # A3 Scan
            # rotate kf to correct for A3
            zero = np.zeros_like(self.A3)
            ones = np.ones_like(self.A3)
            rotMat = np.array([[np.cos(np.deg2rad(self.A3)),np.sin(np.deg2rad(self.A3)),zero],[-np.sin(np.deg2rad(self.A3)),np.cos(np.deg2rad(self.A3)),zero],[zero,zero,ones]])
            q_temp = self.ki-self.kf

            self.q = np.einsum('jki,k...->ji...',rotMat,q_temp)

        self.Q = np.linalg.norm(self.q,axis=0)

    def generateMask(self,maskingFunction = maskFunction, **pars):
        """Generate mask to applied to data in data file
        
        Kwargs:

            - maskingFunction (function): Function called on self.phi to generate mask (default maskFunction)

        All other arguments are passed to the masking function.

        """

        # check if counts attribute is available

        if not hasattr(self,'counts'):
            raise RuntimeError('DataFile does not contain any counts. Look for self.counts but found nothing.')

        if maskingFunction is None:
            self.mask = np.zeros_like(self.counts,dtype=bool)
        else:
            self.mask = maskingFunction(self.phi,**pars)
        
        

    def updateProperty(self,dictionary):
        """Update self with key and values from provided dictionary. Overwrites any properties already present."""
        if isinstance(dictionary,dict):
            for key,item in dictionary.items():
                if key == 'exclude': continue
                if key == 'kwargs': # copy kwargs directly and continue
                    self.kwargs = item
                    continue
                if isinstance(item,Entry):
                    for key2,item2 in item.__dict__.items():
                        item.__dict__[key2] = decode(item2)
                else:
                    item = decode(item)
                    
                self.__setattr__(key,copy.deepcopy(item))
        else:
            raise AttributeError('Provided argument is not of type dictionary. Received instance of type {}'.format(type(dictionary)))


    @_tools.KwargChecker(function=plt.errorbar,include=_tools.MPLKwargs)
    def plotDetector(self,ax=None,applyNormalization=True,**kwargs):
        """Plot intensity as function of twoTheta (and vertical position of pixel in 2D)

        Kwargs:

            - ax (axis): Matplotlib axis into which data is plotted (default None - generates new)

            - applyNormalization (bool): If true, take detector efficiency into account (default True)

            - All other key word arguments are passed on to plotting routine

        """

        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.get_figure()

        
        intensity = self.counts/self.monitor.reshape(-1,1,1)
        if applyNormalization:
            intensity*=1.0/self.normalization

        count_err = np.sqrt(self.counts)
        intensity_err = count_err/self.monitor.reshape(-1,1,1)
        if applyNormalization:
            intensity_err*=1.0/self.normalization
 


        # If data is one dimensional
        if self.twoTheta.shape[1] == 1:
            if not 'fmt' in kwargs:
                kwargs['fmt'] = '.-'

            ax._err = ax.errorbar(self.twoTheta[np.logical_not(self.mask)],intensity[np.logical_not(self.mask)],intensity_err[np.logical_not(self.mask)],**kwargs)
            ax.set_xlabel(r'$2\theta$ [deg]')
            ax.set_ylabel(r'Counts/mon [arb]')

            def format_coord(ax,xdata,ydata):
                if not hasattr(ax,'xfmt'):
                    ax.mean_x_power = _tools.roundPower(np.mean(np.diff(ax._err.get_children()[0].get_data()[0])))
                    ax.xfmt = r'$2\theta$ = {:3.'+str(ax.mean_x_power)+'f} Deg'
                if not hasattr(ax,'yfmt'):
                    ymin,ymax,ystep = [f(ax._err.get_children()[0].get_data()[1]) for f in [np.min,np.max,len]]
                    
                    ax.mean_y_power = _tools.roundPower((ymax-ymin)/ystep)
                    ax.yfmt = r'Int = {:.'+str(ax.mean_y_power)+'f} cts'

                return ', '.join([ax.xfmt.format(xdata),ax.yfmt.format(ydata)])

            ax.format_coord = lambda format_xdata,format_ydata:format_coord(ax,format_xdata,format_ydata)
        else: # plot a 2D image with twoTheta vs z
            # Set all masked out points to Nan
            intensity[self.mask] = np.nan

            if 'colorbar' in kwargs:
                colorbar = kwargs['colorbar']
                del kwargs['colorbar']
            else:
                colorbar = False
            
            ax._pcolormesh = ax.pcolormesh(self.twoTheta,self.pixelPosition[2],np.sum(intensity,axis=0),shading='auto')

            if colorbar:
                ax._col = fig.colorbar(ax._pcolormesh)
                ax._col.set_label('Intensity [cts/Monitor]')
                

            ax.set_xlabel(r'$2\theta$ [deg]')
            ax.set_ylabel(r'z [m]')

        return ax

    @_tools.KwargChecker()
    def save(self,filePath,compression=6):
        """Save data file in hdf format.
        
        Args:

            - filePath (path): Path into which file is to be saved

        Kwargs:

            - compression (int): Compression level used by gzip

        """
        if os.path.exists(filePath):
            raise AttributeError('File already exists! ({})'.format(filePath))

        
        # Recursive function to generate a directory with all entries
        def extractEntries(entry,currentName='',currentDict={},include=[]):
            for key,item in entry.__dict__.items():
                
                if not isinstance(item,Entry):
                    if len(include)>0:
                        if not key in include:
                            continue
                    currentDict[currentName+'/'*(len(currentName)>0)+key] = item
                else:
                    extractEntries(item,currentName+'/'*(len(currentName)>0)+key,currentDict)
                
            return currentDict


        saveDict = extractEntries(self,include=['proposal_id','start_time','title','NX_class'])

        # replace 'Monitor' with 'monitor'
        keys = np.array([[x,x.replace('Monitor','monitor')] if 'Monitor' in x else [0,None] for x in list(saveDict.keys())])
        keys = keys[keys[:,0]!=0]

        for old,new in keys:
            saveDict[new] = saveDict.pop(old)

        # Function to check if entry contains group with specific name
        def contains(entry,groupName):
            splitName = groupName.split('/')
            for sName in splitName:
                if not sName in entry:
                    return False
                entry = entry.get(sName)
            return True


        # 

        with hdf.File(filePath,'w') as f:
            
            # Create correct header info
            f.attrs['NeXus_Version'] = np.string_('4.4.0')
            f.attrs['file_name'] = np.string_(filePath)
            
            
            cT = datetime.datetime.now()
            
            f.attrs['file_time'] = np.string_('{}-{}-{} {}:{}:{}'.format(cT.year,cT.month,cT.day,cT.hour,cT.minute,cT.second))
            f.attrs['instrument'] = np.string_('DMC')
            f.attrs['owner'] = np.string_('Lukas Keller <lukas.keller@psi.ch>')

            entry = f.create_group('entry')
            entry.attrs['NX_class'] = np.string_('NXentry')
            entry.attrs['default'] = np.string_('data')
            for key,value in saveDict.items(): # loop through all pairs
            
                ## Generate all groups with corresponding attributes
                # notice: name under user is not an attribute!
                if (key.split('/')[-1] in ['name','type','signal'] or key.split('/')[-1][:2] == 'NX') and key!='user/name':
                    baseName = '/'.join(key.split('/')[:-1])
                    endName = key.split('/')[-1]
                    # if group doesn't exist, cerate it
                    if not contains(entry,baseName):
                        baseEntry = entry.create_group(baseName)
                    else:
                        baseEntry = entry.get(baseName)
                    
                    # Add the value to the attribute
                    baseEntry.attrs[endName] = value
                        
                
                else:# Take care of all data set structures
                    # Split into base and actual data set name
                    baseName = key.split('/')[:-1]
                    endName = key.split('/')[-1]
                    
                    # Attributes contain '__'
                    if not contains(entry,key) and not '__' in endName:
                        # replace repetition of base name in data set name for all but 'detector_position'
                        if len(baseName)>0 and endName != 'detector_position':
                            endName = endName.replace(baseName[-1]+'_','')
                        
                        # recreate the actual data set name
                        globalName = '/'.join(baseName+[endName])
                        if hasattr(value,'dtype'): # Is a numpy type
                            if len(value.shape)!=0:
                                kwargs = {'compression':"gzip", 'compression_opts':compression}
                            else:
                                kwargs = {}
                            # special shape for Powder data
                            if self.scanType == 'Powder' and endName == 'data':
                                shape = value.shape[1:]
                            else:
                                shape = value.shape
                            entry.create_dataset(globalName,shape = shape, data=value.reshape(shape), **kwargs)

                        elif isinstance(value,str): # If string, save this with correct dtype, i.e. scalar
                            length = max(len(value), 1) # Find length, minimum is 1
                            dset = entry.create_dataset(globalName,(1,),dtype='<S'+str(length))
                            dset[0] = np.string_(value)
                        else: # Catch exceptions
                            raise AttributeError('Unknown data type for',key)
                    elif '__' in endName: # an attribute
                        # replace the '__' in the name, separate out attrName 
                        *name, attrName = endName.replace('__','').split('_')
                        globalName = '/'.join(baseName+['_'.join(name)])
                        entry.get(globalName).attrs[attrName] = value
                    else:
                        raise AttributeError('Unknown error for',key)
            
            # Make the symbolic link between data in the DMC/Detector and Data/Data
            entry['data/data'] = entry['DMC/detector/data']


    def __eq__(self,other):
        return len(self.difference(other))==0
    
    def difference(self,other,keys = set(['sample.name','waveLength','counts','A3','twoTheta','scanType','monitor'])):
        """Return the difference between two data files by keys"""
        dif = []
        if not set(self.__dict__.keys()) == set(other.__dict__.keys()): # Check if same generation and type (hdf or nxs)
            return list(set(self.__dict__.keys())-set(other.__dict__.keys()))

        comparisonKeys = keys
        for key in comparisonKeys:
            skey = self
            okey = other
            while '.' in key:
                baseKey,*keys = key.split('.')
                skey = getattr(skey,baseKey)
                okey = getattr(okey,baseKey)
                key = '.'.join(keys)
            if isinstance(skey,np.ndarray):
                try:
                    if not np.all(np.isclose(skey,okey)):
                        if not np.all(np.isnan(skey),np.isnan(okey)):
                            dif.append(key)
                except (TypeError, AttributeError,ValueError):
                    if np.all(skey!=okey):
                        dif.append(key)
            elif not np.all(getattr(skey,key)==getattr(okey,key)):
                dif.append(key)
        return dif


    @property
    def intensity(self):
        return np.divide(self.counts,self.normalization)

    def InteractiveViewer(self,**kwargs):
        if not self.scanType.lower() in ['a3','powder'] :
            raise AttributeError('Interactive Viewer can only be used for the new data files. Either for powder or for a single crystal A3 scan')
        return InteractiveViewer.InteractiveViewer(self.intensity,self.twoTheta,self.pixelPosition,self.A3,scanParameter = 'A3',scanValueUnit='deg',colorbar=True,**kwargs)










## Dictionary for holding hdf position of attributes. HDFTranslation['a3'] gives hdf position of 'a3'
HDFTranslation = {'sample':'/entry/sample',
                  'sampleName':'/entry/sample/name',
                  'unitCell':'/entry/sample/unit_cell',
                  'intensity':'entry/DMC/detector/intensity',
                  'wavelength':'entry/DMC/monochromator/wavelength',
                  'twoThetaPosition':'entry/DMC/detector/detector_position',
                  'mode':'entry/monitor/mode',
                  'preset':'entry/monitor/preset',
                  'startTime':'entry/start_time',
                  'monitor':'entry/monitor/monitor',
                  'time':'entry/monitor/time',
                  'endTime':'entry/end_time',
                  'comment':'entry/comment',
                  'proposal':'entry/proposal_id',
                  'proposalTitle':'entry/proposal_title',
                  'localContact':'entry/local_contact/name',
                  'proposalUser':'entry/proposal_user/name',
                  'proposalEmail':'entry/proposal_user/email',
                  'user':'entry/user/name',
                  'email':'entry/user/email',
                  'address':'entry/user/address',
                  'affiliation':'entry/user/affiliation',
                  'A3':'entry/sample/rotation_angle',
                  'temperature':'entry/sample/temperature',
                  'magneticField':'entry/sample/magnetic_field',
                  'electricField':'entry/sample/electric_field',
                  'scanCommand':'entry/scancommand',
                  'title':'entry/title',
                  'absoluteTime':'entry/control/absolute_time',
                  'protonBeam':'entry/proton_beam/data'
}
## Default dictionary to perform on loaded data, i.e. take the zeroth element, swap axes, etc

HDFTranslationFunctions = defaultdict(lambda : [])
HDFTranslationFunctions['mode'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['sampleName'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['startTime'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['wavelength'] = [['mean',[]]]
HDFTranslationFunctions['twoThetaPosition'] = [['__getitem__',[0]]]
HDFTranslationFunctions['endTime'] = [['__getitem__',[0]]]
HDFTranslationFunctions['experimentalIdentifier'] = [['__getitem__',[0]]]
HDFTranslationFunctions['comment'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['proposal'] = [['__getitem__',[0]]]
HDFTranslationFunctions['proposalTitle'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['localContact'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['proposalUser'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['proposalEmail'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['user'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['email'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['address'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['affiliation'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['scanCommand'] = [['__getitem__',[0]],['decode',['utf8']]]
HDFTranslationFunctions['title'] = [['__getitem__',[0]],['decode',['utf8']]]



HDFInstrumentTranslation = {
}

HDFInstrumentTranslationFunctions = defaultdict(lambda : [])
# HDFInstrumentTranslationFunctions['counts'] = [['swapaxes',[1,2]]]
HDFInstrumentTranslationFunctions['twoThetaPosition'] = [['mean',]]
HDFInstrumentTranslationFunctions['wavelength'] = [['mean',]]

extraAttributes = ['name','fileLocation']

possibleAttributes = list(HDFTranslation.keys())+list(HDFInstrumentTranslation.keys())+extraAttributes
possibleAttributes.sort(key=lambda v: v.lower())



def getNX_class(x,y,attribute):
    try:
        variableType = y.attrs['NX_class']
    except:
        variableType = ''
    if variableType==attribute:
        return x

def getInstrument(file):
    location = file.visititems(lambda x,y: getNX_class(x,y,b'NXinstrument'))
    return file.get(location)

def shallowRead(files,parameters):

    parameters = np.array(parameters)
    values = []
    possibleAttributes.sort(key=lambda v: v.lower())
    possible = []
    for p in parameters:
        possible.append(p in possibleAttributes)
    
    if not np.all(possible):
        if np.sum(np.logical_not(possible))>1:
            raise AttributeError('Parameters {} not found'.format(parameters[np.logical_not(possible)]))
        else:
            raise AttributeError('Parameter {} not found'.format(parameters[np.logical_not(possible)]))
    
    for file in files:
        vals = {}
        vals['file'] = file
        with hdf.File(file,mode='r') as f:
            instr = getInstrument(f)
            for p in parameters:
                if p == 'name':
                    v = os.path.basename(file)
                    vals[p] = v
                    continue
                elif p == 'fileLocation':
                    v = os.path.dirname(file)
                    vals[p] = v
                    continue
                elif p in HDFTranslation:
                    v = np.array(f.get(HDFTranslation[p]))
                    TrF= HDFTranslationFunctions
                elif p in HDFInstrumentTranslation:
                    v = np.array(instr.get(HDFInstrumentTranslation[p]))
                    TrF= HDFInstrumentTranslationFunctions
                else:
                    raise AttributeError('Parameter "{}" not found'.format(p))
                for func,args in TrF[p]:
                    try:
                        v = getattr(v,func)(*args)
                    except (IndexError,AttributeError):
                        warnings.warn('Parameter "{}" not found in file "{}"'.format(p,file))
                        v = None
                        
                vals[p] = v
        values.append(vals)

    return values