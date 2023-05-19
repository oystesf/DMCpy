import  os
# sys.path.append(r'C:\Users\lass_j\Documents\Software\DMCpy')
from Tutorial_Class import Tutorial


def Tester():
    from DMCpy import DataSet,DataFile,_tools
    import os

    # Give file number and folder the file is stored in.
    scanNumbers = '12153'
    folder = 'data/SC'
    year = 2022
        
    # Create complete filepath
    file = os.path.join(os.getcwd(),_tools.fileListGenerator(scanNumbers,folder,year=year)[0]) 

    # Load data file with corrected twoTheta
    df = DataFile.loadDataFile(file)
    
    # run the Interactive Viewer
    IA1 = df.InteractiveViewer()
    IA1.set_clim(0,20)
    IA1.set_clim_zIntegrated(0,1000)

    IA1.fig.savefig(r'docs/Tutorials/InteractiveViewer/InteractiveViewer1.png',format='png',dpi=300)

    # Use above data file in data set. Must be inserted as a list
    ds = DataSet.DataSet([df])

    # subtract backround in a A3 range. This must be done on the dataSet level and act on every dataFile in the dataSet
    #ds.subtractBkgRange(50,100)
    # this has a bug...

    # run the Interactive Viewer
    IA2 = ds[0].InteractiveViewer()
    IA2.set_clim(0,20)
    IA2.set_clim_zIntegrated(0,1000)

    IA2.fig.savefig(r'docs/Tutorials/InteractiveViewer/InteractiveViewer2.png',format='png',dpi=300)

    # change index of A3
    IA2.plotSpectrum(index=114)

    IA2.fig.savefig(r'docs/Tutorials/InteractiveViewer/InteractiveViewer2_114.png',format='png',dpi=300)

    

    
    
    
title = 'Interactive Viewer'

introText = 'In a single crystal experiment, the first step is to gain an overview of the system. This is most often done '\
+'by performing an A3 scan with the sample in a specific scattering plane. Due to the 2D detector of DMC, such an A3 scan produces '\
+'a 3D set of measured data points. In the frame of reference of the instrument, the majority of the covered volume is '\
+'in the Qx-Qy plane, i.e. with Qz close to zero. A single A3 slices corresponds to a curved line in th Qx-Qy '\
+' together with a symmetrically curved line in Qz. This sheet is then rotated around the origin with each A3 step.'\
+'The Interactive Viewer sums intensities in one direction to give 2D figures of measured intensities. '\
+'In total 3 figures are then generated: summer over z, summed over A3 and summed over 2theta. '\
+'The graphics are interactive and by clicking in the summed over z you change the A3. '\
+'\n\n'\
+'A useful feature is to use a defined A3 range to subtract background from a sample can. '\
+'The given area is averaged and subtracted from the entire data set. '\
+'This does not work well with A3-dependent powder rings and background subtracted data should not be used for cuts and integration. '\

outroText = 'The above code takes the data from the A3 scan file dmc2022n008540, and plot the Interactive Viewer. '\
+'It also demonstrate how a A3 region (in step) can be subtracted to clean up the data. '\
+'\n\nFirst data overview \n'\
+'\n.. figure:: InteractiveViewer1.png \n  :width: 50%\n  :align: center\n\n '\
+'\n\nSecond data overview with background subtraction\n'\
+'\n.. figure:: InteractiveViewer2.png \n  :width: 50%\n  :align: center\n\n '\
+'\n\nThird data overview with background subtraction and A3 step 114\n'\
+'\n.. figure:: InteractiveViewer2_114.png \n  :width: 50%\n  :align: center\n\n '\

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('InteractiveViewer',introText,outroText,Tester,fileLocation = os.path.join(os.getcwd(),r'docs/Tutorials/InteractiveViewer'))

def test_InteractiveViewer():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()