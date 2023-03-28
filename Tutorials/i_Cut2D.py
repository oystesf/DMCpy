import sys
#sys.path.append(r'C:\Software\DMCpy\DMCpy')
from Tutorial_Class import Tutorial
import os

def Tester():
    import matplotlib.pyplot as plt
    from DMCpy import DataSet,DataFile,_tools
    import numpy as np
    import os, copy
    
    # Give file number and folder the file is stored in.
    scanNumbers = '8540' 
    folder = 'data/SC'
    year = 2022
        
    # Create complete filepath
    file = os.path.join(os.getcwd(),_tools.fileListGenerator(scanNumbers,folder,year=year)[0]) 

    # Load data file with corrected twoTheta
    df = DataFile.loadDataFile(file)
    
    # Use above data file in data set. Must be inserted as a list
    ds = DataSet.DataSet([df])

    # load UB matrix
    ds.loadSample(r'data/SC/UB.bin')

    # define 2D cut
    width = 0.5
    
    points = np.array([[0.0,0.0,0.0],
            [0.0,0.0,1.0],
            [1.0,1.0,0.0]])
        
    s = copy.deepcopy(ds.sample[0]) 
    
    projectionVector1 = points[1]-points[0]
    projectionVector2 = points[2]-points[0]
    projectionVector3 = np.array([-1.0,1.0,0.0])
    
    newPoints = [np.dot(np.dot(ds.sample[0].ROT,s.UB),point) for point in points]
    
    totalRotMat, translation = _tools.calculateRotationMatrixAndOffset2(newPoints)

    s.UB= np.dot(totalRotMat,s.UB)
    
    ax = ds.createRLUAxes(sample = s)

    ax._step = np.dot(points[0],projectionVector3)*1
    
    xMult = 1.42 #1.41549208
    yMult = np.linalg.norm(ds[0].sample.calculateHKLToQxQyQz(1,1,0))          
        
    step = 0.02
    
    kwargs = {
        'xBins' : np.arange(-1.0,3.0,step/xMult)*xMult,
        'yBins' : np.arange(-0.0,3.0,step/yMult)*yMult,
        'steps' : 151,
        'rlu' : True,
        'rmcFile' : True,
        'colorbar' : True,             
        }
    
    ax,returndata,bins = ds.plotQPlane(points=points,width=width,ax=ax,**kwargs) 
    
    ax.grid(True,zorder=20)
    ax.set_xticks_base(1)
    ax.set_yticks_base(1)
     
    ax.set_clim(0,0.001)
    
    planeFigName = 'docs/Tutorials/2Dcut'
    plt.savefig(planeFigName+'.png', bbox_inches="tight",dpi=300)

    kwargs = {
        'rmcFileName' : planeFigName+'.txt'
        }
    
    ax.to_csv(planeFigName+'.csv',**kwargs)
    
   
     
    
title = 'Cut2D'

introText = 'After inspecting the scattering plane, we want to perform cuts along certain directions.'\
+' In this tutorial, we demonstrate the cut2D function. Cuts can be made given by hkl or Qx, Qy, Qz.'\
+' The width of the cut orthogonal to the plane can be adjusted by the keywords width and width.'\
+' The grid the cut is projected on is given by the xBins and yBins keywords.'\


outroText = 'The above code takes the data from the A3 scan file dmc2021n000590, align and plot the scattering plane.'\
+'Then three cuts along different directions are performed.'\
+'\n\nFirst data overview with Qz slightly positive and Qx and Qy in the plane\n'\
+'\n.. figure:: 2Dcut.png \n  :width: 50%\n  :align: center\n\n '\

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('Cut2D',introText,outroText,Tester,fileLocation = os.path.join(os.getcwd(),r'docs/Tutorials'))

def test_Cut2D():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()