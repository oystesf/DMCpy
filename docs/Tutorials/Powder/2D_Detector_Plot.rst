Detector Overview Powder
^^^^^^^^^^^^^^^^^^^^^^^^
The simplets data set on the DMC instrument is that of a powder measured with only one setting. This results in a 'one shot' data set where scattering intensity is measured as a function of scattering angle and position out of plane. This can be visualized in the frame of reference of the instrument by the following code:

.. code-block:: python
   :linenos:

   from DMCpy import DataFile, _tools
   
   # Give file number and folder the file is stored in.
   scanNumbers = '578'
   folder = 'data'
   
   # Give correct two theta
   twoThetaOffset = 18.0
   
   # Create complete filepath
   file = os.path.join(os.getcwd(),_tools.fileListGenerator(scanNumbers,folder)[0]) 
   
   # Load data file with corrected twoTheta
   df = DataFile.loadDataFile(file,twoThetaPosition=twoThetaOffset)
   
   #Plot detector
   ax = df.plotDetector()
   
   fig = ax.get_figure()
   fig.set_size_inches(20, 2.5)
   fig.savefig('figure0.png',format='png')
   

At the current stage, a normalization file for the 2D detector is not present and thus a dummy is created. Running the above code generates the following images showing neutron intensity as function of 2Theta and out of plane position:
 .. figure:: Plot2DPowderDetector_new_and_better.png
  :width: 100%
  :align: center

 