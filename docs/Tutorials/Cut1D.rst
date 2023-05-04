Cut1D
^^^^^
After inspecting the scattering plane, we want to perform cuts along certain directions. In this tutorial, we demonstrate the cut1D function. Cuts can be made given by hkl or Qx, Qy, Qz. The width of the cut can be adjusted by the keywords width and widthZ. Note that this function is not intended for obtaining integrated intensities of Bragg peaks.

.. code-block:: python
   :linenos:

   import matplotlib.pyplot as plt
   from DMCpy import DataSet,DataFile,_tools
   import numpy as np
   import os
   
   # Give file number and folder the file is stored in.
   scanNumbers = '12153-12154' 
   folder = 'data/SC'
   year = 2022
   path = os.path.join(os.getcwd(),folder)  
  
   filePath = _tools.fileListGenerator(scanNumbers,folder,year=year) 
   
   # # # load dataFiles
   dataFiles = [DataFile.loadDataFile(dFP) for dFP in filePath]
         
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
   
   positionVector,I,err,ax = ds.plotCut1D([0.333,0.333,-0.5],[0.333,0.333,0.5],**kwargs)
   fig = ax.get_figure()
   fig.savefig('figure0.png',format='png')
   
   #export of cut to text file
   saveData = np.column_stack([positionVector[0],positionVector[1],positionVector[2],I,err])
   np.savetxt(os.path.join(path,'cut.txt'),saveData,header='h,k,l,I,err',delimiter=',')
   

The above code takes the data from a A3 scan, and align it by the alignToRefs function.Then one cuts across the 1/3,1/3,l direction. The example also demonstrate how kwargs can be given to the functions to adjust the apperance of the figure. 

The cut is diplayed below 

.. figure:: Cut1.png 
  :width: 50%
  :align: center

 