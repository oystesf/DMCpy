import  os
# sys.path.append(r'C:\Users\lass_j\Documents\Software\DMCpy')
from Tutorial_Class import Tutorial


def Tester():
    from DMCpy import DataSet,DataFile,_tools
    import matplotlib.pyplot as plt
    import numpy as np

    # Give file number and folder the file is stored in.
    scanNumbers = '12105-12106' 
    folder = 'data/SC'
    year = 2022
  
    filePath = _tools.fileListGenerator(scanNumbers,folder,year=year) 
            
    # load data files and make data set
    ds = DataSet.DataSet(filePath,forcePowder=True)
    
    ax,bins,Int,Int_err,monitor = ds.plotTwoTheta()
    planeFigName = 'docs/Tutorials/forecePowder'
    plt.savefig(planeFigName+'.png',format='png', dpi=300)

    # make centres for bins
    Centres=0.5*(bins[1:]+bins[:-1])

    # export
    stacked_array = np.column_stack((Centres.flatten(), Int.flatten(), Int_err.flatten()))

    # Export the stacked array to an ASCII file
    np.savetxt('docs/Tutorials/Force_powder.xy', stacked_array, delimiter='\t', fmt='%s')
        
    
    
    
title = 'Force powder'

introText = 'This tutorial demonstrate how a single crystal dataset can be converted to a powder dataset and plotted and exported. '\



outroText = 'The above code takes a single crystal data file and converts it into a powder file. This means that all A3 are merged. '\
+'Note that we do not load the datafiles first into DataFiles, but they are loaded directly into a DataSet. '\
+'\n\nDiffraction pattern from single crystal data. \n'\
+'\n.. figure:: forecePowder.png \n  :width: 50%\n  :align: center\n\n '\

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('forcePowder',introText,outroText,Tester,fileLocation = os.path.join(os.getcwd(),r'docs/Tutorials/'))

def test_forcePowder():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()