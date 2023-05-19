#import sys
#sys.path.append(r'C:\Software\DMCpy\DMCpy')
from Tutorial_Class import Tutorial
import os

def Tester():
    import matplotlib.pyplot as plt
    from DMCpy import DataSet,DataFile,_tools
    import numpy as np
    import os

    # Give file number and folder the file is stored in.
    scanNumbers = '12105-12106' 
    folder = 'data/SC'
    year = 2022
  
    filePath = _tools.fileListGenerator(scanNumbers,folder,year=year) 

    unitCell = np.array([ 7.218, 7.218, 18.183, 90.0, 90.0, 120.0])

    # # # load dataFiles
    dataFiles = [DataFile.loadDataFile(dFP,unitCell = unitCell) for dFP in filePath]
            
    # load data files and make data set
    ds = DataSet.DataSet(dataFiles)

    # Define Q coordinates and HKL for the coordinates. 
    q2 = [-1.2240,-1.6901,-0.0175]
    q1 = [-1.4275,1.0299,-0.0055]
    HKL2 = [0,0,6]
    HKL1 = [1,1,0]
    
    # this function uses two coordinates in Q space and align them to corrdinates in HKL space
    ds.alignToRefs(q1=q1,q2=q2,HKL1=HKL1,HKL2=HKL2)

    # Here we do a cut over the (440) reflection by the cut1D function. 
    # cut1D takes start and end point as lists.
   
    kwargs = {
                'width' : 0.1,
                'widthZ' : 0.5,
                'stepSize' : 0.005,
                'rlu' : True,
                'optimize' : False,
                'marker' : 'o',
                'color' : 'green',
                'markersize' : 8,
                'mew' : 1.5,
                'linewidth' : 1.5,
                'capsize' : 3,
                'linestyle' : (0, (1, 1)),
                'mfc' : 'white',
                }
    
    positionVector,I,err,ax = ds.plotCut1D([1.333,1.333,-0.5],[1.333,1.333,0.5],**kwargs)
    fig = ax.get_figure()
    fig.savefig(r'docs/Tutorials/Cut1.png',format='png',dpi=300)

    #export of cut to text file
    if False:
        path = os.path.join(os.getcwd(),folder)  
        saveData = np.column_stack([positionVector[0],positionVector[1],positionVector[2],I,err])
        np.savetxt(os.path.join(path,'cut.txt'),saveData,header='h,k,l,I,err',delimiter=',')
        
      
title = 'Cut1D'

introText = 'After inspecting the scattering plane, we want to perform cuts along certain directions.'\
+' In this tutorial, we demonstrate the cut1D function. Cuts can be made given by hkl or Qx, Qy, Qz.'\
+' The width of the cut can be adjusted by the keywords width and widthZ.'\
+' The unit of width and widthZ is AA-1.'\

outroText = 'The above code takes the data from a A3 scan, and align it by the alignToRefs function.'\
+'Then one cuts across the 4/3,4/3,l direction. '\
+'The example also demonstrate how kwargs can be given to the functions to adjust the apperance of the figure. '\
+'\n\nThe cut is diplayed below \n'\
+'\n.. figure:: Cut1.png \n  :width: 50%\n  :align: center\n\n '\

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('Cut1D',introText,outroText,Tester,fileLocation = os.path.join(os.getcwd(),r'docs/Tutorials'))

def test_Cut1D():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()