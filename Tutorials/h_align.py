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


    # alignment to spesific Qx,Qy,Qz corrdinates. 
    # directions along x and y is also given for the alignment
    if False:
        ds.alignToRef(np.array([-0.447,-0.914,-0.003]),np.array([1,0,0]),np.array([0,1,0]))

    # automatic alignment to a scattering plane.
    # generate a peak list and find scattering normal from cros products
    # rotate so scattering normal is along 001 and rotate to get reflection along x-axis
    if False:
        ds.autoAlignScatteringPlane(np.array([0.0,0.0,1.0]),inPlaneRef=np.array([0.0,2.0,0.0]),threshold=1000)

    #
    if False:
        P1 = [1,0,0]
        P2 = [0,1,0]
        P3 = [0,0,1]
        ds.autoAlignToRef(scatteringNormal=np.array(P3),inPlaneRef=np.array(P1),planeVector2=np.array(P2),threshold=10)

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
+'autoAlignScatteringPlane has the following method which is useful when many peaks are measured. \n'\
+'1) Perform a 3D binning of data in to equi-sized bins with size (dx,dy,dz) \n'\
+'2) Peaks are defined as all positions having intensities>threshold \n'\
+'3) These peaks are clustered together if closer than 0.02 1/AA and centre of gravity using intensity is applied to find common centre. \n'\
+'4) Above step is repeated with custom distanceThreshold \n'\
+'5) Plane normals are found as cross products between all vectors connecting all found peaks -> Gives a list of approximately NPeaks*(NPeaks-1)*(NPeaks-2) \n'\
+'6) Plane normals are clustered and most common is used \n'\
+'7) Peaks are rotated into the scattering plane \n'\
+'8) Within the plane all found peaks are projected along the nice plane vectors and the peak having the scattering length closest to an integer multiple of either is chosen for alignment \n'\
+'9) Rotation within the plane is found by rotating the found peak either along x or y  depending on which projection vector was closest \n'\
+'10) Sample is updated with found rotations. \n\n'\


outroText = '  '\


introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('Alignment',introText,outroText,Tester,fileLocation = os.path.join(os.getcwd(),r'docs/Tutorials/View3D'))

def test_Alignment():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()