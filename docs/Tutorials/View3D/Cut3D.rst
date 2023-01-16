Cut3D
^^^^^
After inspecting the scattering plane, we want to perform cuts along certain directions. In this tutorial, we demonstrate the cut1D function. Cuts can be made given by hkl or Qx, Qy, Qz. The width of the cut can be adjusted by the keywords width and widthZ.

.. code-block:: python
   :linenos:

   from DMCpy import DataSet,DataFile
   import matplotlib.pyplot as plt
   import numpy as np
   import os
   
   folder = 'data'
   file = r'dmc2021n009003.hdf'
   
   df = DataFile.loadDataFile(os.path.join(folder,file))
   
   # Use above data file in data set. Must be inserted as a list
   ds = DataSet.DataSet([df])
   
   ds.autoAlignScatteringPlane(scatteringNormal=np.array([1,-1,0],dtype=float))
   
   Viewer = ds.Viewer3D(0.03,0.03,0.03)
   
   # Set the color bar limits to 0 and 60
   Viewer.set_clim(0,20)
   
   
   # Find the number of steps and set viewer to middel value
   # This can also be done interactively in the viewer by pressing up or down,
   # or by scrolling the mouse wheel or clicking the sliding bar.
   zSteps = Viewer.Z.shape[-1]
   Viewer.setPlane(int(zSteps/2)-1)
   
   fig = Viewer.ax.get_figure()
   fig.savefig('figure0.png',format='png')
   
   # First we do a cut over the (440) reflection by the cut1D function. 
   # cut1D takes start and end point as lists.
   positionVector,I,ax = ds.plotCut1D([3.8,3.8,0],[4.2,4.2,0],width=0.2,widthZ=0.2)
   fig = ax.get_figure()
   fig.savefig('figure1.png',format='png')
   
   # Cut over (004) to (008)
   positionVector,I,ax = ds.plotCut1D([0.3,0.2,3],[0.4,0.3,8.1],width=0.5,widthZ=0.2)
   fig = ax.get_figure()
   fig.savefig('figure2.png',format='png')
   
   # Cut over (4-x,4-x,x)
   positionVector,I,ax = ds.plotCut1D([4.2,4.2,-0.2],[-0.2,-0.2,4.2],width=0.5,widthZ=0.3)
   fig = ax.get_figure()
   fig.savefig('figure3.png',format='png')
   

The above code takes the data from the A3 scan file dmc2021n000590, align and plot the scattering plane.Then three cuts along different directions are performed.

First data overview with Qz slightly positive and Qx and Qy in the plane

.. figure:: CenterMiddel_cut.png 
  :width: 50%
  :align: center

 

First cut

.. figure:: Cut1.png 
  :width: 50%
  :align: center

 

Second cut

.. figure:: Cut2.png 
  :width: 50%
  :align: center

 

Thrid cut

.. figure:: Cut3.png 
  :width: 50%
  :align: center

 