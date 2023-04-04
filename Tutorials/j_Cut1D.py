import sys
#sys.path.append(r'C:\Software\DMCpy\DMCpy')
from Tutorial_Class import Tutorial
import os

def Tester():
    import matplotlib.pyplot as plt
    from DMCpy import DataSet,DataFile,_tools
    import numpy as np
    import os
    
    #file = r'C:/Users/lass_j/Documents/DMC_2021/dmc2021n009003.hdf'

    # Give file number and folder the file is stored in.
    scanNumbers = '8540' 
    folder = 'data/SC'
    path = os.path.join(os.getcwd(),folder)
    year = 2022
        
    # Create complete filepath
    file = os.path.join(os.getcwd(),_tools.fileListGenerator(scanNumbers,folder,year=year)[0]) 

    # Load data file with corrected twoTheta
    df = DataFile.loadDataFile(file)
    
    # Use above data file in data set. Must be inserted as a list
    ds = DataSet.DataSet([df])
    
    # load UB matrix
    ds.loadSample(r'data/SC/UB.bin')

    # Here we do a cut over the (440) reflection by the cut1D function. 
    # cut1D takes start and end point as lists.
   
    kwargs = {
                'width' : 0.2,
                'widthZ' : 0.2,
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
    
    positionVector,I,err,ax = ds.plotCut1D([0.975,0.975,0],[1.075,1.075,0],**kwargs)
    fig = ax.get_figure()
    fig.savefig(r'docs/Tutorials/Cut1.png',format='png',dpi=300)

    #export of cut to text file
    saveData = np.column_stack([positionVector[0],positionVector[1],positionVector[2],I,err])
    np.savetxt(os.path.join(path,'cut.txt'),saveData,header='h,k,l,I,err',delimiter=',')
    
      
title = 'Cut1D'

introText = 'After inspecting the scattering plane, we want to perform cuts along certain directions.'\
+' In this tutorial, we demonstrate the cut1D function. Cuts can be made given by hkl or Qx, Qy, Qz.'\
+' The width of the cut can be adjusted by the keywords width and widthZ.'


outroText = 'The above code takes the data from the A3 scan file dmc2021n008540, and align it by a UB matrix loaded from disk.'\
+'Then one cuts across the 110 relection is performed. '\
+'\n\nThe cut is diplayed below \n'\
+'\n.. figure:: Cut1.png \n  :width: 50%\n  :align: center\n\n '\

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('Cut1D',introText,outroText,Tester,fileLocation = os.path.join(os.getcwd(),r'docs/Tutorials'))

def test_Cut1D():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()