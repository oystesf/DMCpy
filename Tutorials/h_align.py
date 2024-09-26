import os
# sys.path.append(r'C:\Users\lass_j\Documents\Software\DMCpy')
from Tutorial_Class import Tutorial


def Tester():
    from DMCpy import DataSet,DataFile,_tools
    import numpy as np
    
    # Give file number and folder the file is stored in.
    scanNumbers = '12153-12154' 
    folder = 'data/SC'
    year = 2022
  
    filePath = _tools.fileListGenerator(scanNumbers,folder,year=year) 
        
    # we can add the unit cell to the data files or directly to DMCpy when we load the data
    unitCell = np.array([ 7.218, 7.218, 18.183, 90.0, 90.0, 120.0])

    # Alternative to add unit cell to files   
    if False:
        _tools.giveUnitCellToHDF(filePath,unitCell)

    # # # load dataFiles with unit cell
    dataFiles = [DataFile.loadDataFile(dFP,unitCell = unitCell) for dFP in filePath]
            
    # load data files and make data set
    ds = DataSet.DataSet(dataFiles)

    # The recommended function for alignment is alignToRefs, which takes two coordinates in Q and the corresponding hkl vectors
    q1 = [-0.447,-0.914,-0.003]
    q2 = [-1.02,-0.067,-0.02]
    HKL1 = [1,0,0]
    HKL2 = [0,1,0]
    
    # this function uses two coordinates in Q space and align them to corrdinates in HKL space
    ds.alignToRefs(q1=q1,q2=q2,HKL1=HKL1,HKL2=HKL2)

    # To find the A3, A4 and z values of a reflection, we can use calcualteHKLToA3A4Z
    # The function work on both DataSet and DataFile level
    ds.calcualteHKLToA3A4Z(1,1,0)

    # save UB to file
    if False:
        _tools.saveSampleToDesk(ds[0].sample,r'UB.bin')

    # # # load UB from file
    if False:
        rlu = True
        ds.loadSample(r'UB.bin')


    
    
title = 'Alignment'

introText = 'A UB matrix is needed to convert the measured data into hkl-space. '\
+'UB matrices is stored in the sample object in DMCpy and can be saved and loaded as binary files. '\
+'DMC only measure one scattering plane and conventional indexing will not work as information in one direction will be missing. '\
+'DMCpy therefore has a few alternative methods for generating UB matrices. \n'\
+'alignToRefs is the recommended method for alignment. It is a method that takes two QxQyQz coordinates, which is used to tilt and rotate the data. \n\n'\
+'alignToRef is a method which takes one spesific QxQyQz coordinates, which is used to tilt and rotate the data. \n\n'\


outroText = '  '\


introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('Alignment',introText,outroText,Tester,fileLocation = os.path.join(os.getcwd(),r'docs/Tutorials/View3D'))

def test_Alignment():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()