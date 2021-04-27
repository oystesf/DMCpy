import functools
import numpy as np
from difflib import SequenceMatcher
import os.path


MPLKwargs = ['agg_filter','alpha','animated','antialiased or aa','clip_box','clip_on','clip_path','color or c','contains','dash_capstyle','dash_joinstyle','dashes','drawstyle','figure','fillstyle','gid','label','linestyle or ls','linewidth or lw','marker','markeredgecolor or mec','markeredgewidth or mew','markerfacecolor or mfc','markerfacecoloralt or mfcalt','markersize or ms','markevery','path_effects','picker','pickradius','rasterized','sketch_params','snap','solid_capstyle','solid_joinstyle','transform','url','visible','xdata','ydata','zorder']

def KwargChecker(function=None,include=None):
    """Function to check if given key-word is in the list of accepted Kwargs. If not directly therein, checks capitalization. If still not match raises error
    with suggestion of closest argument.
    
    Args:
    
        - func (function): Function to be decorated.

    Raises:

        - AttributeError
    """
    def KwargCheckerNone(func):
        @functools.wraps(func)
        def newFunc(*args,**kwargs):
            argList = extractArgsList(func,newFunc,function,include)
            checkArgumentList(argList,kwargs)
            returnval = func(*args,**kwargs)
            return returnval
        newFunc._original = func
        newFunc._include = include
        newFunc._function = function
        return newFunc
    return KwargCheckerNone

def extractArgsList(func,newFunc,function,include):
    N = func.__code__.co_argcount # Number of arguments with which the function is called
    argList = list(newFunc._original.__code__.co_varnames[:N]) # List of arguments
    if not function is None:
        if isinstance(function,(list,np.ndarray)): # allow function kwarg to be list or ndarray
            for f in function:
                for arg in f.__code__.co_varnames[:f.__code__.co_argcount]: # extract all arguments from function
                    argList.append(str(arg))
        else: # if single function
            for arg in function.__code__.co_varnames[:function.__code__.co_argcount]:
                argList.append(str(arg))
    if not include is None:
        if isinstance(include,(list,np.ndarray)):
            for arg in include:
                argList.append(str(arg))
        else:
            argList.append(str(include))
        argList = list(set(argList)) # Cast to set to remove duplicates
        argList.sort() #  Sort alphabetically
    return argList

def checkArgumentList(argList,kwargs):
    notFound = []
    for key in kwargs:
        if key not in argList:
            similarity = np.array([SequenceMatcher(None, key.lower(), x.lower()).ratio() for x in argList])
            maxVal = np.max(similarity)
            maxId = np.argmax(similarity)
            notFound.append('Key-word argument "{}" not understood. Did you mean "{}"?'.format(key,argList[maxId]))
    if len(notFound)>0:
        if len(notFound)>1:
            errorMsg = 'The following key-word arguments are not understood:\n'
            errorMsg+='\n'.join(notFound)
        else:
            errorMsg = notFound[0]
        error = AttributeError(errorMsg)
        raise error

@KwargChecker()
def numberStringGenerator(fileNames,instrumentName='dmc'):
    names = np.array([os.path.splitext(os.path.basename(df))[0] for df in fileNames])
    # Find base name and remove extension
    if len(fileNames) != 1:
        prefix = os.path.commonprefix(list(names))
        
        if instrumentName in prefix:
            # Remove all non-zero digits from prefix
            while prefix[-1]!='0' and prefix[-1]!='n':
                prefix = prefix[:-1]
            year = int(prefix[len(instrumentName):len(instrumentName)+4])
            numbers = np.array([n[len(prefix):] for n in names],dtype=int)
            sortNumbers = np.sort(numbers)
            diff = np.diff(sortNumbers)
            separators = list(np.arange(len(diff))[diff>1]+1) # add one due to diff removing 1 lenght
            groups = []
            if len(separators) == 0:
                groups.append('-'.join([str(sortNumbers[0]),str(sortNumbers[-1])]))
            else:
                separators.insert(0,0)
                separators.append(-1)
                for start,stop in zip(separators[:-1],separators[1:]):
                    if stop == -1:
                        group = sortNumbers[start:]
                    else:
                        group = sortNumbers[start:stop]
                    if len(group)>2:
                        groups.append('-'.join([str(group[0]),str(group[-1])]))
                    elif len(group)==2:
                        groups.append(','.join(group.astype(str)))
                    else:
                        groups.append(str(group[0]))
            files = ','.join(groups)
    return year,files

@KwargChecker()
def fileListGenerator(numberString,folder,year=2021, format = None, instrument = 'dmc'):
    """Function to generate list of data files.
    
    Args:
        
        - numberString (str): List if numbers separated with comma and dashes for sequences.
        
        - folder (str): Folder of wanted data files.
        
    Kwargs:

        - year (int): Year of wanted data files (default 2018)

        - format (str): format of data files (default None, but dmc if instrument is provided)

        - instrument (str): Instrument to be used to determine format string (default dmc)
        
    returns:
        
        - list of strings: List containing the full file string for each number provided.
        
    Example:
        >>> numberString = '201-205,207-208,210,212'
        >>> files = fileListGenerator(numberString,'data/',2018)
        ['data/dmc2018n000201.hdf', 'data/dmc2018n000202.hdf', 
        'data/dmc2018n000203.hdf', 'data/dmc2018n000204.hdf', 
        'data/dmc2018n000205.hdf', 'data/dmc2018n000207.hdf', 
        'data/dmc2018n000208.hdf', 'data/dmc2018n000210.hdf', 
        'data/dmc2018n000212.hdf']
    """
        
    splits = numberString.split(',')
    dataFiles = []
    if format is None: # If no user specified format is provided
        if instrument == 'dmc':
            format = 'dmc{:d}n{:06d}.hdf'
        else:
            raise AttributeError('Provided instrument "{}" not understood'.format(instrument))


    for sp in splits:
        isRange = sp.find('-')!=-1
        
        if isRange:
            spSplits = sp.split('-')
            if len(spSplits)>2:
                raise AttributeError('Sequence "{}" not understood - too many dashes.'.format(sp))
            startNumber = int(spSplits[0])
            endNumber = int(spSplits[1])
            numbers = np.arange(startNumber,endNumber+1)    
        else:
            numbers = [int(sp)]

        dataFiles.append([os.path.join(folder,format.format(year,x)) for x in numbers])
    return list(np.concatenate(dataFiles))