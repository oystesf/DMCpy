#import sys
# sys.path.append(r'C:\Users\lass_j\Documents\Software\DMCpy')
from Tutorial_Class import Tutorial
import os

def Tester():
    from DMCpy import DataFile,DataSet, _tools
    
    # Create a DataFile and DataSet for 565
    file = r'data\dmc2021n000565.hdf'
    
    df = DataFile.loadDataFile(file)
    ds = DataSet.DataSet(df)
    
    
    # Create a DataFile and DataSet for 565 with correct twoTheta
    twoThetaOffset = 18.0
    
    df = DataFile.loadDataFile(file,twoThetaPosition=twoThetaOffset)
    ds = DataSet.DataSet(df)
    
    # Create a DataFile and DataSet with _tools.fileListGenerator
    scanNumbers = '578'
    folder = 'data'

    # Create complete filepath
    file = os.path.join(os.getcwd(),_tools.fileListGenerator(scanNumbers,folder)[0]) 

    df = DataFile.loadDataFile(file,twoThetaPosition=twoThetaOffset)
    ds = DataSet.DataSet(df)
    
    # If we want to load several DataFiles in the DataSet
    dataFiles = [DataFile.loadDataFile(dFP,twoThetaPosition=twoThetaOffset) for dFP in _tools.fileListGenerator(scanNumbers,folder)]
    
    ds = DataSet.DataSet(dataFiles)

    
title = 'Make a DataFile and DataSet'

introText = 'In this tutorial we demonstrate how to make DataFiles and DataSets in DMCpy. You create a DataFile by the loadDataFile function.'\
+ ' The input for loadDataFile is file name and path as a string. In addition, can arguments that act on the DataFile be give, *e.g.*  *twoThetaPosition*.'\
+ ' The _tools.fileListGenerator is a useful tool to create a list of DataFiles with complete path. The input is the short number of the Datafile and path.'\
+ ' Several DataFiles can be added into one DataSet. This is done by giving DataSet a list of DataFiles: DataSet(dataFiles)'\

outroText = ''

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('Make Data File',introText,outroText,Tester,fileLocation = os.path.join(os.getcwd(),r'docs/Tutorials'))

def test_Make_Data_File():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()