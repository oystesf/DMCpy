Two Theta Diffractogram
^^^^^^^^^^^^^^^^^^^^^^^
When a powder has been measured, in one or more settings, these can be combined into a common DataFet. The follwing code does exactly this, for a single DataFile which currently only contains zeros. Two different settings for the binning method is used *correctedTwoTheta* equal to *True* and *False*. When *False* a naive summation across the 2D detector is performed where the out-of-plane component is not taken into account. That is, summation is performed vertically on the detector. For powder patterns around 90\ :sup:`o`, this is only a very minor error, but for scattering close to the direct beam a significant error is introduced. Instead, utilizing *correctedTwoTheta = True* is the correct way. The scattering 3D vector is calculated for each individual pixel on the 2D detector and it's length is calculated.

.. code-block:: python
   :linenos:

   from DMCpy import DataSet
   import numpy as np
   import DMCpy
   
   file = r'Path\To\Data\Folder\dmc2021n000565.hdf'
   
   
   ds = DataSet.DataSet(file)
   
   # Generate a two theta plot utilizing the corrected 2Theta values
   ax,bins,Int,Int_err,monitor = ds.plotTwoTheta()
   fig = ax.get_figure()
   fig.savefig('figure0.png',format='png')
   
   # Generate a two theta plot utilizing the corrected 2Theta values
   ax2,bins2,Int2,Int_err2,monitor2 = ds.plotTwoTheta(correctedTwoTheta=False)
   fig2 = ax2.get_figure()
   fig2.savefig('figure1.png',format='png')
   

Running the above code generates the two following, similar looking, diffractograms utilizing the corrected and uncorrected twoTheta positions respectively
 .. figure:: TwoThetaPowderCorrected.png
  :width: 50%
  :align: center


 .. figure:: TwoThetaPowderUncorrected.png
  :width: 50%
  :align: center

