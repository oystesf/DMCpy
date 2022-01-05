import sys
sys.path.append(r'C:\Users\lass_j\Documents\Software\DMCpy')
from Tutorial_Class import Tutorial


def Tester():
    from DMCpy import DataFile
    import numpy as np
    import DMCpy
    
    file = r'C:/Users/lass_j/Documents/DMC_2021/dmc2021n000565.hdf'
    
    df = DataFile.DataFile(file)
    
    ax = df.plotDetector()
    
    fig = ax.get_figure()
    fig.savefig(r'C:/Users/lass_j/Documents/Software/DMCpy/docs/Tutorials/Powder/Plot2DPowderDetector.png',format='png',dpi=300)
    
title = 'Detector Overview Powder'

introText = 'The simplets data set on the DMC beam line is that of a powder measured with only one setting. This results '\
   + 'in a \'one shot\' data set where scattering intensity is measured as a function of scattering angle and position '\
   + 'out of plane. This can be visualized in the frame of reference of the instrument by the following code:'


outroText = 'At the current stage, a normalization file for the 2D detector is not present and thus a dummy is created. '\
    +'Running the above code generates the following images showing neutron intensity as function of 2Theta and out of plane position:'\
+'\n .. figure:: Plot2DPowderDetector.png\n  :width: 30%\n  :align: center\n\n '

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('2D Detector Plot',introText,outroText,Tester,fileLocation = r'C:/Users/lass_j/Documents/Software/DMCpy/docs/Tutorials/Powder')

def test_2D_Detector_Plot():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()