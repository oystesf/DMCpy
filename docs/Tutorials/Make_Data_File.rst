Make a DataFile and DataSet
^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this tutorial we demonstrate how to make DataFiles and DataSets in DMCpy. You create a DataFile by the loadDataFile function. The input for loadDataFile is file name and path as a string. In addition, can arguments that act on the DataFile be give, *e.g.*  *twoThetaPosition*. The _tools.fileListGenerator is a useful tool to create a list of DataFiles with complete path. The input is the short number of the Datafile and path. Several DataFiles can be added into one DataSet. This is done by giving DataSet a list of DataFiles: DataSet(dataFiles)

.. code-block:: python
   :linenos:

   from DMCpy import DataFile,DataSet, _tools
   import numpy as np
   
   # Create a DataFile and DataSet for 565
   file = r'data\dmc2021n000565.hdf'
   
   df = DataFile.loadDataFile(file)
   ds = DataSet.DataSet(df)
   
   
   # Create a DataFile and DataSet for 565 with correct twoTheta
   twoThetaOffset = 1.0
   
   df = DataFile.loadDataFile(file,twoThetaPosition=twoThetaOffset)
   ds = DataSet.DataSet(df)
   
   # Create a DataFile and DataSet with _tools.fileListGenerator
   scanNumbers = '578'
   folder = 'data'
   
   # Create complete filepath
   file = os.path.join(os.getcwd(),_tools.fileListGenerator(scanNumbers,folder)[0]) 
   
   df = DataFile.loadDataFile(file,twoThetaPosition=twoThetaOffset)
   ds = DataSet.DataSet(df)
   
   # If we want to load several DataFiles in the DataSet
   dataFiles = [DataFile.loadDataFile(dFP,twoThetaPosition=twoThetaOffset) for dFP in _tools.fileListGenerator(scanNumbers,folder)]
   
   ds = DataSet.DataSet(dataFiles)
   
   
   # We can also add a unit cell to the dataFiles when loaded:
   scanNumbers = '12153' 
   folder = 'data/SC'
   year = 2022
  
   filePath = _tools.fileListGenerator(scanNumbers,folder,year=year) 
   
   unitCell = np.array([ 7.218, 7.218, 18.183, 90.0, 90.0, 120.0])
   
   # # # load dataFiles
   dataFiles = [DataFile.loadDataFile(dFP,unitCell = unitCell) for dFP in filePath]
   

