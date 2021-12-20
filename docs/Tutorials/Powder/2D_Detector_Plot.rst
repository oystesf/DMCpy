Detector Overview Powder
^^^^^^^^^^^^^^^^^^^^^^^^
The simplets data set on the DMC beam line is that of a powder measured with only one setting. This resluts in a 'one shot' data set where scattering intensity is measured as a function of scattering angle and position out of plane. This can be visualized in the frame of reference of the instrument by the following code:

.. code-block:: python
   :linenos:

   from DMCpy import DataFile
   import numpy as np
   import DMCpy
   
   file = r'Path\To\Data\Folder'
   
   calib2021 = {'limits':np.array([1]),
        'names':np.array(['Mockup']),
        'Mockup':np.ones((1152,128))}
   # The shape of the mochup data is given by the detector (128*9, 128)
   
   DMCpy.calibrationDict[2021] = calib2021
   
   df = DataFile.DataFile(file)
   df.monitor = 1.0
   
   ax = df.plotDetector()
   
   fig = ax.get_figure()
   fig.savefig('figure0.png',format='png')
   

At the current stage, a normalization file for the 2D detector is not present and thus a dummy is created. Running the above code generates the following images showing neutron intensity as function of 2Theta and out of plane position:
 .. figure:: Plot2DPowderDetector.png
  :width: 30%
  :align: center

 At some point a more impressive data set is to be plotted...