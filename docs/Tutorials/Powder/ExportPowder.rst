Export of diffraction patterns
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The software can export powder patterns to .dat files in PSI format and to .xye files. This is done by built in functions. The following fuctions are avaliable: *export()*, *add()*, *export_from()*, *export_from_to()* to export measured data to . In addition, the function *export_help()* can be used to general help for export functions. Help for all export function can also be printed by e.g. *help(export)*. In this tutorial we examplify the use of the export functions and the various keywords for the functions.
 
 
--------------------------------
 
Properties of export functions: 
 
---------------------------------
 
export: Exports files, will be merged if - is used, and exported one by one if space is used. Examples: export 296-297 298 will merge 296 and 297, while 298 is exported by itself. 
 
exportAll: All scans will be exported individually. Example: exportAll 280-290 will export all files in the range individually. 
 
add: All scans will be added. Example: add 296-297 300 will merge all the scans. 
 
sortExport: Will go sort all scans by sampleName and title, and group them. Scans with same sampleName and title will be merged. Example: sortExport 280-290. sortExport can also ignore files by ignore=XXX. Example: sortExport 290-300 ignore=295 will export 290-294,296-300. 
 
sleepExport: Runs sortExport with a time interval given in seconds. If no start value is given, it will run over all files in the folder. An end value can also be given but is not mandatory or recommended. Example: sleepExport 600, sleepExport 600 start=270 end=300. sleepExport can also ignore files by ignore=XXX. Example: sleepExport 20 start=290 end=300 ignore=295 will export 290-294,296-300. 
 
-----------------------------------------------
 
Integration arguments: Default value is given. 
 
------------------------------------------------
 
dTheta=0.125 - stepsize for binning of output data. Example:  export 296-297 dTheta=0.175 
 
useMask=True - export files with and without an angular mask. Example: export 296-297 useMask=False does not export _HR files where an angular mask is used. 
 
maxAngle=5 - the angle of the angular mask. Example: export 296-297 maxAngle=3 
 
onlyHR=False - export files only with a mask. export 296-297 onlyHR =True only export HR files made with an angular mask. 
 
applyNormalization=True - use vanadium calibration to correct for pixel efficacy. Example: export 296-297 applyNormalization=False does not use the calibration for the export of the scan. 
 
correctedTwoTheta=True - integrate in Q or vertically on the detector. Example:  export 296-297 correctedTwoTheta=False gives vertical integration of the scan. 
 
twoThetaOffset=0 - shit of two theta if a4 in the file is incorrect. Not recommended to use. Example: export 296-297 twoThetaOffset=3 
 
 
-------------------------------------------------------------------------------
 
Filename arguments for including information in the name of the exported file: 
 
--------------------------------------------------------------------------------
 
temperature=False -  Include temperature in the name of the output file. It can be useful if exporting scans with the same sampleName and title, and you dont want to overwrite the file. Example: export 296-297 temperature=True 
 
fileNumber=False - Include file numbers in the name of output file. Can be useful if exporting scans with same sampleName and title, and you dont want to overwrite the file. Example: export 296-297 fileNumber=True 
 
waveLength=False - Include wavelength in the name of output file. Can be useful for experiments with different wavelengths. Example: export 296-297 waveLength=True 
 
magField=False: Include magnetic field in the name of output file. 
 
elField=False: Include electric field in the name of output file. 
 
addTitle=None - add text to the automatically generated title. export 296-297 addTitle=addedText would add the addedText to the automatically generated file name. 
 
 
-----------------
 
Other arguments: 
 
------------------
 
hourNormalization=True - export files normalized to one hour on monitor. Example: export 296-297 hourNormalization =False, dont export normalized files. 
 
onlyNorm=True - export only files that are normalized. export 296-297 onlyNorm=False, do export non-normalized data as well as normalized. 
 
outFile=None - name for outputfile. If this argument is used, the arguments for automatic filename will be ignored. Example: export 296-297 outFile=newfilename 
 
folder=None - folder of the hdf file. Is read from json file. 
 
outFolder=None - folder for storing the output files. Example: export 296-297 outFolder=commissioning. 
 
PSI=True - export of dat files in PSI format. Example: export 296-297 PSI=False, dont export PSI format files. 
 
xye=False - export of xye files. Example: export 296-297 xye=True, do export xye files. 
 
-------------------------------------
 
Examples fo use of export functions: 
 
--------------------------------------
 


.. code-block:: python
   :linenos:

   from DMCpy import DataSet
      
   # print general help for exporting data.
   DataSet.export_help()
   
   # print help for add() function. 
   help(DataSet.add)    
   
   
   # export(): Exports 565 and 578 induyvidually. The step size for the exported files is 0.25. The data files are located in 'data/' and the exported files are stored in 'docs/Tutorials/Powder'. 
   DataSet.export(565,578,dTheta=0.25,folder=r'data/',outFolder=r'docs/Tutorials/Powder',dataYear=2021)
   # exports .dat and .xye files of 565 and 578 induvidually.
   
   # export(): Export can also be used to merge files. Here [567,568,570,571] is merged, '570-573' is merged and (574,575) is merged.
   # In the file names of the exported files, the file numbers are given, and not the sample name. 
   DataSet.export([567,568,570,571],'570-573',(574,575),sampleName=False,fileNumber=True,folder=r'data/',outFolder=r'docs/Tutorials/Powder',dataYear=2021)
   # exports .dat and .xye files of 567_568_570_571, 570-573, 574_575
   
   # add(): Add the files 565,578,579,585,586,587,575 and export one file named 'added_files'. The data files are located in 'data/' and the exported files are stored in 'docs/Tutorials/Powder'. 
   DataSet.add(565,578,579,(585),'586-587',[575],outFile='added_files',folder=r'data/',outFolder=r'docs/Tutorials/Powder',dataYear=2021)
   # exports 'added_files.dat' and 'added_files.xye'
   
   # export_from_to(): exports all files from 578 to 582. The files are located in 'data/' and the exported files are stored in 'docs/Tutorials/Powder'. 
   # For the automatic filename, sample name is not included, but the file number is included. 
   DataSet.export_from_to(578,582,sampleName=False,fileNumber=True,folder=r'data/',outFolder=r'docs/Tutorials/Powder',dataYear=2021)
   # exports .dat and .xye files of 578, 579, 580, 581, 582
   
   # subtract(): Subtract two data files from each other. Must have same binning. In this case, only .dat files are subtracted as xye=False. 
   DataSet.subtract('DMC_579','DMC_578',xye=False,outFile=r'subtracted_file',folder=r'docs/Tutorials/Powder',outFolder=r'docs/Tutorials/Powder')
   # create subtracted_file.dat
   

 