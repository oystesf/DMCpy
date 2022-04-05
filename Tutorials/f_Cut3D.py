import sys
sys.path.append(r'C:\Software\DMCpy\DMCpy')
from Tutorial_Class import Tutorial


def Tester():
    from DMCpy import DataSet,DataFile
    import matplotlib.pyplot as plt
    import numpy as np
    
    file = r'C:\Software\DMCpy\DMCpy\data\SC\dmc2021n009003.hdf'
    
    df = DataFile.loadDataFile(file)
    
    # Use above data file in data set. Must be inserted as a list
    ds = DataSet.DataSet([df])
    
    ds.autoAlignScatteringPlane(scatteringNormal=np.array([1,-1,0],dtype=float))

    Viewer = ds.Viewer3D(0.03,0.03,0.03)
    
    # Set the color bar limits to 0 and 60
    Viewer.set_clim(0,20)
    
    
    # Find the number of steps and set viewer to middel value
    # This can also be done interactively in the viewer by pressing up or down,
    # or by scrolling the mouse wheel or clicking the sliding bar.
    zSteps = Viewer.Z.shape[-1]
    Viewer.setPlane(int(zSteps/2)-1)
    
    fig = Viewer.ax.get_figure()
    fig.savefig(r'C:\Software\DMCpy\DMCpy/docs/Tutorials/View3D/CenterMiddel_cut.png',format='png',dpi=300)
    
    # First we do a cut over the (440) reflection by the cut1D function. 
    # cut1D takes start and end point as lists.
    positionVector,I = ds.cut1D([3.8,3.8,0],[4.2,4.2,0],width=0.2,widthZ=0.2)
    plt.figure(2)
    plt.plot(positionVector[1],I,linestyle=':', marker='o')
    plt.ylabel('Int [arb. units]')
    plt.xlabel('(4-h,4-h,0) [h]')
    plt.savefig(r'C:\Software\DMCpy\DMCpy/docs/Tutorials/View3D/Cut1.png',format='png',dpi=300)
    
    # Cut over (004) to (008)
    positionVector,I = ds.cut1D([0.3,0.2,3],[0.4,0.3,8.1],width=0.5,widthZ=0.2)
    plt.figure(3)
    plt.plot(positionVector[2],I,linestyle=':', marker='o')
    plt.ylabel('Int [arb. units]')
    plt.xlabel('(0,0,l) [l]')
    plt.savefig(r'C:\Software\DMCpy\DMCpy/docs/Tutorials/View3D/Cut2.png',format='png',dpi=300)

    # Cut over (4-x,4-x,x)
    positionVector,I = ds.cut1D([4.2,4.2,-0.2],[-0.2,-0.2,4.2],width=0.5,widthZ=0.3)
    plt.figure(4)
    plt.plot(positionVector[2],I,linestyle=':', marker='o')    
    plt.ylabel('Int [arb. units]')
    plt.xlabel('(4-x,4-x,x) [x]')
    plt.savefig(r'C:\Software\DMCpy\DMCpy/docs/Tutorials/View3D/Cut3.png',format='png',dpi=300)
   
    
    
    
title = 'Cut3D'

introText = 'After inspecting the scattering plane, we want to perform cuts along certain directions.'\
+' In this tutorial, we demonstrate the cut1D function. Cuts can be made given by hkl or Qx, Qy, Qz.'\
+' The width of the cut can be adjusted by the keywrods width and widthZ.'


outroText = 'The above code takes the data from the A3 scan file dmc2021n000590, align and plot the scattering plane.'\
+'Then three cuts along different directions are performed.'\
+'\n\nFirst data overview with Qz slightly positive and Qx and Qy in the plane\n'\
+'\n.. figure:: CenterMiddel_cut.png \n  :width: 50%\n  :align: center\n\n '\
+'\n\nFirst cut\n'\
+'\n.. figure:: Cut1.png \n  :width: 50%\n  :align: center\n\n '\
+'\n\nSecond cut\n'\
+'\n.. figure:: Cut2.png \n  :width: 50%\n  :align: center\n\n '\
+'\n\nThrid cut\n'\
+'\n.. figure:: Cut3.png \n  :width: 50%\n  :align: center\n\n '

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('Cut3D',introText,outroText,Tester,fileLocation = r'C:\Software\DMCpy\DMCpy/docs/Tutorials/View3D')

def test_Cut3D():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()