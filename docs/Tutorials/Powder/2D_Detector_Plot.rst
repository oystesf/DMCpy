Detector Overview Powder
^^^^^^^^^^^^^^^^^^^^^^^^
The simplets data set on the DMC instrument is that of a powder measured with only one setting. This results in a 'one shot' data set where scattering intensity is measured as a function of scattering angle and position out of plane. This can be visualized in the frame of reference of the instrument by the following code:

.. code-block:: python
   :linenos:

   from DMCpy import DataFile, _tools
   
   # Give file number and folder the file is stored in.
   scanNumbers = '1285'
   folder = 'data'
   year = 2022
      
   # Create complete filepath
   file = os.path.join(os.getcwd(),_tools.fileListGenerator(scanNumbers,folder,year=year)[0]) 
   
   # Load data file with corrected twoTheta
   df = DataFile.loadDataFile(file)
   
   #Plot detector with defualt mask
   ax = df.plotDetector()
   ax.invert_xaxis()
   
   cmax = 0.01
   ax._pcolormesh.set_clim(0,cmax)
   
   fig = ax.get_figure()
   fig.set_size_inches(20, 2.5)
   fig.tight_layout()
   fig.savefig('figure0.png',format='png')
   
   #Plot detector without masks
   df.generateMask(lambda x: DataFile.maskFunction(x,maxAngle=180.0),replace=True)
   
   ax2 = df.plotDetector()
   ax2.invert_xaxis()
   ax2._pcolormesh.set_clim(0,cmax)
   
   fig2 = ax2.get_figure()
   fig2.set_size_inches(20, 2.5)
   fig2.tight_layout()
   fig2.savefig('figure1.png',format='png')
   
   #Plot detector with 5 deg angular mask
   df.generateMask(lambda x: DataFile.maskFunction(x,maxAngle=5.0),replace=True)
   
   ax3 = df.plotDetector()
   ax3.invert_xaxis()
   ax3._pcolormesh.set_clim(0,cmax)
   
   fig3 = ax3.get_figure()
   fig3.set_size_inches(20, 2.5)
   fig3.tight_layout()
   fig3.savefig('figure2.png',format='png')
   
   #Plot detector with 5 deg angular mask
   df.generateMask(lambda x: DataFile.maskFunction(x,maxAngle=10.0),replace=True)
   
   ax4 = df.plotDetector()
   ax4.invert_xaxis()
   ax4._pcolormesh.set_clim(0,cmax)
   
   fig4 = ax4.get_figure()
   fig4.set_size_inches(20, 2.5)
   fig4.tight_layout()
   fig4.savefig('figure3.png',format='png')
   
   #Plot detector with line mask
   df.generateMask(lambda x: DataFile.maskFunction(x,maxAngle=180.0),replace=True)
   
   df.mask[0,10:20,:] = True
   df.mask[0,:,50:60] = True
   
   ax5 = df.plotDetector()
   ax5.invert_xaxis()
   ax5._pcolormesh.set_clim(0,cmax)
   
   fig5 = ax5.get_figure()
   fig5.set_size_inches(20, 2.5)
   fig5.tight_layout()
   fig5.savefig('figure4.png',format='png')
   

The software use the defualt normalization from the calibration file which is matched with the file number. As default a mask for the second top line of the detector is used as it has an issue. The code show how the mask can be removed, how an angular mask can be added, and how a line mask cna be added. Running the above code generates the following images showing neutron intensity as function of 2Theta and out of plane position: Note that two theta is negative, which is defualt at DMC. 
 .. figure:: Plot2DPowderDetector_new_and_better.png
  :width: 80%
  :align: center

 
 .. figure:: Plot2DPowderDetector_new_and_better_no_mask.png
  :width: 80%
  :align: center

 
 .. figure:: Plot2DPowderDetector_new_and_better_5deg_mask.png
  :width: 80%
  :align: center

 
 .. figure:: Plot2DPowderDetector_new_and_better_10deg_mask.png
  :width: 80%
  :align: center

 
 .. figure:: Plot2DPowderDetector_new_and_better_line_mask.png
  :width: 80%
  :align: center

 