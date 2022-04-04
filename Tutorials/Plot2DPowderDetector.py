import sys
# sys.path.append(r'C:\Users\lass_j\Documents\Software\DMCpy')
from Tutorial_Class import Tutorial
import os

def Tester():
    from DMCpy import DataFile, _tools
    
    # Give file number and folder the file is stored in.
    scanNumbers = '578'
    folder = 'data'
    
    # Give correct two theta
    twoThetaOffset = 18.0
    
    # Create complete filepath
    file = os.path.join(os.getcwd(),_tools.fileListGenerator(scanNumbers,folder)[0]) 

    # Load data file with corrected twoTheta
    df = DataFile.loadDataFile(file,twoThetaPosition=twoThetaOffset)
    
    #Plot detector
    ax = df.plotDetector()
    
    fig = ax.get_figure()
    fig.set_size_inches(20, 2.5)
    fig.savefig(r'docs/Tutorials/Powder/Plot2DPowderDetector_new_and_better.png',format='png',dpi=300)
    
title = 'Detector Overview Powder'

introText = 'The simplets data set on the DMC instrument is that of a powder measured with only one setting. This results '\
   + 'in a \'one shot\' data set where scattering intensity is measured as a function of scattering angle and position '\
   + 'out of plane. This can be visualized in the frame of reference of the instrument by the following code:'


outroText = 'At the current stage, a normalization file for the 2D detector is not present and thus a dummy is created. '\
    +'Running the above code generates the following images showing neutron intensity as function of 2Theta and out of plane position:'\
+'\n .. figure:: Plot2DPowderDetector_new_and_better.png\n  :width: 100%\n  :align: center\n\n '

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('2D Detector Plot',introText,outroText,Tester,fileLocation = os.path.join(os.getcwd(),r'docs/Tutorials/Powder'))

def test_2D_Detector_Plot():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()