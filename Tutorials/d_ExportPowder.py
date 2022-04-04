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
    DataSet.export(565,578,dTheta=0.25,folder=r'data/',outFolder=r'docs/Tutorials/Powder')
    # exports .dat and .xye files of 565 and 578 induvidually.

    # export(): Export can also be used to merge files. Here [567,568,570,571] is merged, '570-573' is merged and (574,575) is merged.
    # In the file names of the exported files, the file numbers are given, and not the sample name. 
    DataSet.export([567,568,570,571],'570-573',(574,575),sampleName=False,fileNumber=True,folder=r'data/',outFolder=r'docs/Tutorials/Powder')
    # exports .dat and .xye files of 567_568_570_571, 570-573, 574_575
    
    # add(): Add the files 565,578,579,585,586,587,575 and export one file named 'added_files'. The data files are located in 'data/' and the exported files are stored in 'docs/Tutorials/Powder'. 
    DataSet.add(565,578,579,(585),'586-587',[575],outFile='added_files',folder=r'data/',outFolder=r'docs/Tutorials/Powder')
    # exports 'added_files.dat' and 'added_files.xye'
    
    # export_from_to(): exports all files from 578 to 582. The files are located in 'data/' and the exported files are stored in 'docs/Tutorials/Powder'. 
    # For the automatic filename, sample name is not included, but the file number is included. 
    DataSet.export_from_to(578,582,sampleName=False,fileNumber=True,folder=r'data/',outFolder=r'docs/Tutorials/Powder')
    # exports .dat and .xye files of 578, 579, 580, 581, 582
    
    # subtract(): Subtract two data files from each other. Must have same binning. In this case, only .dat files are subtracted as xye=False. 
    DataSet.subtract('DMC_579','DMC_578',xye=False,outFile=r'subtracted_file',folder=r'docs/Tutorials/Powder',outFolder=r'docs/Tutorials/Powder')
    # create subtracted_file.dat
    
    
title = 'Export of diffraction patterns'

introText = 'The software can export powder patterns to .dat files in PSI format and to .xye files. This is done by built in functions. '\
+'The following fuctions are avaliable: *export()*, *add()*, *export_from()*, *export_from_to()* to export measured data to . '\
+'In addition, the function *export_help()* can be used to general help for export functions. '\
+'Help for all export function can also be printed by e.g. *help(export)*. '\
+'In this tutorial we examplify the use of the export functions and the various keywords for the functions.\n \n'\
+'Properties of export functions:\n'\
+' - export(): For export of induvidual sets of scan files. Files can be merged by [] or "" notation, i.e. list or strings.\n'\
+' - add(): The function adds/merge all the files given independent on the notation.\n'\
+' - export_from(): For export of all data files in a folder after a startfile.\n'\
+' - export_from_to(): It exports all files between and including two given file numbers.\n'\
+' - export_list(): Takes a list and export all the files separatly. If a list is given inside the list, the files will be merged.\n'\
+' - subtract(): Takes two file names and subtract the corresponding .dat and .xye files. The function act on exported data files, not on raw data.\n \n'\
+'Most important kewords:\n'\
+' - sampleName (bool): Include sample name from raw file in filename. Default is True.\n'\
+' - dTheta (float): Stepsize of binning if no bins is given (default is 0.125).\n'\
+' - outFile (str): String for name of outfile (given without extension). If not given, an automatic file name will be generated.\n'\
+' - folder (str): Path to directory for data files, default is current working directory.\n'\
+' - outFolder (str): Path to folder data will be saved. Default is current working directory.\n \n'\
+'Example: export(578, dTheta=0.25)\n \n'\
+'Both PSI and xye format files are exported as default. They can be deactivated by the following keywords.\n'\
+' - PSI (bool): Use PSI format. Default is True.\n'\
+' - xye (bool): Use xye format. Default is True.\n \n'\
+'Example: export(578, PSI=False) \n \n'\
+'File names for exported files are by default the sample named stored in the raw file. This can be changed with the following keywords:\n \n'\
+' - sampleName (bool): Use sample name stored in raw file in file name of exported data. Default is True.\n'\
+' - temperature (bool): Include temperature in filename. Default is False.\n'\
+' - fileNumber (bool): Include sample number in filename. Default is False.\n'\
+' - magneticField (bool): Include magnetic field in filename. Default is False.\n'\
+' - electricField (bool): Include electric field in filename. Default is False.\n \n'\
+'Example: export(578, sampleName=False, fileNumber=True)\n \n'\
+'Examples fo use of export functions: \n \n'


outroText = ' '
    

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('ExportPowder',introText,outroText,Tester,fileLocation = (os.path.join(os.getcwd(),r'docs/Tutorials/Powder'))) 

def test_ExportPowder():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()