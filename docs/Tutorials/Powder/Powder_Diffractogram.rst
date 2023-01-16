Plot of diffraction patterns
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When a powder sample has been measured at DMC it is saved in hdf files. Several DataFiles can be combined into a common DataSet and plotted. The follwing code takes a DatsSet, here consisting of one single DataFile, and plot it. Two different settings for the binning method is used *correctedTwoTheta* equal to *True* and *False*. When *False* a naive summation across the 2D detector is performed where the out-of-plane component is not taken into account. That is, summation is performed vertically on the detector. For powder patterns around 90\ :sup:`o`, this is only a very minor error, but for scattering close to the direct beam a significant error is introduced. Instead, utilizing *correctedTwoTheta = True* is the correct way. The scattering 3D vector is calculated for each individual pixel on the 2D detector and it's length is calculated.

.. code-block:: python
   :linenos:

   from DMCpy import DataSet,DataFile, _tools
   
   # To plot powder data we give the file number, or list of filenumbers as a string and the folder of the raw data
   scanNumbers = '578'
   folder = 'data'
   
   # In this case, we have a offset of twoTheta of 18 degrees. We correct this by changeing the twoThetaOffset for all dataFiles
   twoThetaOffset = 18.0
   
   # a list of dataFiles are generated with loadDataFile running over all the dataFiles generated from _tools.fileListGenerator and twoThetaOffset acts on the dataFile
   dataFiles = [DataFile.loadDataFile(dFP,twoThetaPosition=twoThetaOffset) for dFP in _tools.fileListGenerator(scanNumbers,folder)]
   
   # We then create a data set based on the data files
   ds = DataSet.DataSet(dataFiles)
   
   # We can also give the step size for the integration. Default is 0.2 
   dTheta = 0.125
   
   # Generate a diffraction pattern where the 2D detector is integrated in Q-space
   ax,bins,Int,Int_err,monitor = ds.plotTwoTheta(dTheta=dTheta)
   ax.set_title('Integrated in Q')
   fig = ax.get_figure()
   fig.savefig('figure0.png',format='png'),r'docs/Tutorials/Powder/TwoThetaPowderQ.png'),format='png',dpi=300)
   
   # Generate a diffraction pattern where the 2D detector is integrated vertically
   ax2,bins2,Int2,Int_err2,monitor2 = ds.plotTwoTheta(correctedTwoTheta=False,dTheta=dTheta)
   ax2.set_title('Integrated vertically')
   fig2 = ax2.get_figure()
   fig2.savefig('figure1.png',format='png'),r'docs/Tutorials/Powder/TwoThetaPowderVertical.png'),format='png',dpi=300)
   

Running the above code generates the two following, similar looking, diffractograms utilizing the corrected and uncorrected twoTheta positions respectively. We highlight the reduced noice and the slightly sharper peaks in the corrected image.The down-up glitches of the diffraction pattern is from the interface between the detector sections.
 .. figure:: TwoThetaPowderQ.png
  :width: 50%
  :align: center


 .. figure:: TwoThetaPowderVertical.png
  :width: 50%
  :align: center

