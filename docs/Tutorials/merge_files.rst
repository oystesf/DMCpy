Viewer 3D
^^^^^^^^^
To load two data files that cover the same A3 range is slower than loading one single file. Therefore it is recommended to merge datafiles that covers the same A3 range. It is not required that the data files are of the same A3 range, but they should overlap.The code below is an example of merging of data files  together with a symmetrically curved line in Qz. This sheet is then rotated around the origin with each A3 step.

.. code-block:: python
   :linenos:

   from DMCpy import _tools
   import os
   
   # file numbers that should be merged
   mergeNumbers = ['8540,8553']
   saveFileList = ['merged_file.hdf']
   year = 2022
   
   folder = 'data/SC'
   
   for numbers,saveFileName in zip(mergeNumbers,saveFileList):
      print(numbers)
      dataFilesList = _tools.fileListGenerator(numbers,os.path.join(os.getcwd(),folder),year=year)
      print(dataFilesList)
      _tools.merge(dataFilesList, os.path.join(os.getcwd(),saveFileName)) 
   

The above code takes the data from the A3 scan file dmc2022n008540 and dmc2022n008553, and merge them. In this case the files cover the exact same A3 range, but it is not a requirement. Here the merging is done in a for loop so more files can easily be added. 