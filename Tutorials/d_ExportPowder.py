import sys
# sys.path.append(r'C:\Users\lass_j\Documents\Software\DMCpy')
from Tutorial_Class import Tutorial
import os
# import numpy as np

def Tester():
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
    
    
title = 'Export of diffraction patterns'

introText = 'The software can export powder patterns to .dat files in PSI format and to .xye files. This is done by built in functions. '\
+'The following fuctions are avaliable: *export()*, *add()*, *export_from()*, *export_from_to()* to export measured data to . '\
+'In addition, the function *export_help()* can be used to general help for export functions. '\
+'Help for all export function can also be printed by e.g. *help(export)*. '\
+'In this tutorial we examplify the use of the export functions and the various keywords for the functions.\n \n \n'\
+'-'*len('Properties of export functions: ')+'\n \n'\
+'Properties of export functions: \n \n'\
+'-'*len('Properties of export functions:  ')+'\n \n'\
+'export: Exports files, will be merged if - is used, and exported one by one if space is used. Examples: export 296-297 298 will merge 296 and 297, while 298 is exported by itself. \n \n'\
+'exportAll: All scans will be exported individually. Example: exportAll 280-290 will export all files in the range individually. \n \n'\
+'add: All scans will be added. Example: add 296-297 300 will merge all the scans. \n \n'\
+'sortExport: Will go sort all scans by sampleName and title, and group them. Scans with same sampleName and title will be merged. Example: sortExport 280-290. sortExport can also ignore files by ignore=XXX. Example: sortExport 290-300 ignore=295 will export 290-294,296-300. \n \n'\
+'sleepExport: Runs sortExport with a time interval given in seconds. If no start value is given, it will run over all files in the folder. An end value can also be given but is not mandatory or recommended. Example: sleepExport 600, sleepExport 600 start=270 end=300. sleepExport can also ignore files by ignore=XXX. Example: sleepExport 20 start=290 end=300 ignore=295 will export 290-294,296-300. \n \n'\
+'-'*len('Integration arguments: Default value is given. ')\
+'\n \n'+'Integration arguments: Default value is given. \n \n'\
+'-'*len('Integration arguments: Default value is given.  ')+'\n \n'\
+'dTheta=0.125 - stepsize for binning of output data. Example:  export 296-297 dTheta=0.175 \n \n'\
+'useMask=True - export files with and without an angular mask. Example: export 296-297 useMask=False does not export _HR files where an angular mask is used. \n \n'\
+'maxAngle=5 - the angle of the angular mask. Example: export 296-297 maxAngle=3 \n \n'\
+'onlyHR=False - export files only with a mask. export 296-297 onlyHR =True only export HR files made with an angular mask. \n \n'\
+'applyNormalization=True - use vanadium calibration to correct for pixel efficacy. Example: export 296-297 applyNormalization=False does not use the calibration for the export of the scan. \n \n'\
+'correctedTwoTheta=True - integrate in Q or vertically on the detector. Example:  export 296-297 correctedTwoTheta=False gives vertical integration of the scan. \n \n'\
+'twoThetaOffset=0 - shit of two theta if a4 in the file is incorrect. Not recommended to use. Example: export 296-297 twoThetaOffset=3 \n \n \n'\
+'-'*len('Filename arguments for including information in the name of the exported file: ')\
+'\n \n'+'Filename arguments for including information in the name of the exported file: \n \n'\
+'-'*len('Filename arguments for including information in the name of the exported file:  ')+'\n \n'\
+'temperature=False -  Include temperature in the name of the output file. It can be useful if exporting scans with the same sampleName and title, and you dont want to overwrite the file. Example: export 296-297 temperature=True \n \n'\
+'fileNumber=False - Include file numbers in the name of output file. Can be useful if exporting scans with same sampleName and title, and you dont want to overwrite the file. Example: export 296-297 fileNumber=True \n \n'\
+'waveLength=False - Include wavelength in the name of output file. Can be useful for experiments with different wavelengths. Example: export 296-297 waveLength=True \n \n'\
+'magField=False: Include magnetic field in the name of output file. \n \n'\
+'elField=False: Include electric field in the name of output file. \n \n'\
+'addTitle=None - add text to the automatically generated title. export 296-297 addTitle=addedText would add the addedText to the automatically generated file name. \n \n \n'\
+'-'*len('Other arguments: ')+'\n \n'\
+'Other arguments: \n \n'\
+'-'*len('Other arguments:  ')+'\n \n'\
+'hourNormalization=True - export files normalized to one hour on monitor. Example: export 296-297 hourNormalization =False, dont export normalized files. \n \n'\
+'onlyNorm=True - export only files that are normalized. export 296-297 onlyNorm=False, do export non-normalized data as well as normalized. \n \n'\
+'outFile=None - name for outputfile. If this argument is used, the arguments for automatic filename will be ignored. Example: export 296-297 outFile=newfilename \n \n'\
+'folder=None - folder of the hdf file. Is read from json file. \n \n'\
+'outFolder=None - folder for storing the output files. Example: export 296-297 outFolder=commissioning. \n \n'\
+'PSI=True - export of dat files in PSI format. Example: export 296-297 PSI=False, dont export PSI format files. \n \n'\
+'xye=False - export of xye files. Example: export 296-297 xye=True, do export xye files. \n \n'\
+'-'*len('Examples fo use of export functions: ')\
+'\n \n'+'Examples fo use of export functions: \n \n'\
+'-'*len('Examples fo use of export functions:  ')+'\n \n'


outroText = ' '
    

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('ExportPowder',introText,outroText,Tester,fileLocation = (os.path.join(os.getcwd(),r'docs/Tutorials/Powder'))) 

def test_ExportPowder():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()