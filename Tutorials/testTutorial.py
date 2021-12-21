import sys 
sys.path.append('/home/lass/Dropbox/PhD/Software/DMCpy/')

from Tutorial_Class import Tutorial


def Tester():
    import numpy as np
    import matplotlib.pyplot as plt

    fig,ax = plt.subplots()
    fig.savefig(r'C:/Users/lass_j/Documents/Software/DMCpy/docs/Tutorials/TEST.png',format='png',dpi=300)
    
title = 'Test of Tutorials!'

introText = 'This is a simple test script to check that all is working as expected. Below should be an image of an empty axis...'\
+' if not, then Houston we have a problem '

outroText = 'Showcasing functionality\n'+len('Showcasing functionality')*'-'+'\nThis should be the showcasing...'\
+'An example is shown in the above code generating the figure below:'\
+'\n .. figure:: TEST.png\n  :width: 50%\n  :align: center\n\n'

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('Testing',introText,outroText,Tester,fileLocation = r'C:/Users/lass_j/Documents/Software/DMCpy/docs/Tutorials')

def test_Testing():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()