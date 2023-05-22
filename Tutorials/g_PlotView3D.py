import  os
# sys.path.append(r'C:\Users\lass_j\Documents\Software\DMCpy')
from Tutorial_Class import Tutorial


def Tester():
    from DMCpy import DataSet,DataFile,_tools
    
    # Give file number and folder the file is stored in.
    scanNumbers = '12153-12154' 
    folder = 'data/SC'
    year = 2022
  
    filePath = _tools.fileListGenerator(scanNumbers,folder,year=year) 

    # # # load dataFiles
    dataFiles = [DataFile.loadDataFile(dFP) for dFP in filePath]
            
    # load data files and make data set
    ds = DataSet.DataSet(dataFiles)

    # plot the data with 3D Viewer
    Viewer = ds.Viewer3D(0.01,0.01,0.01,rlu=False)
    
    # Set the color bar limits to 0 and 0.001
    Viewer.set_clim(0,0.001)

    # set axes to be equal
    Viewer.ax.axis('equal')
    
    # Find the number of steps and set viewer to middel value
    # This can also be done interactively in the viewer by pressing up or down,
    # or by scrolling the mouse wheel or clicking the sliding bar.
    zSteps = Viewer.Z.shape[-1]
    Viewer.setPlane(int(zSteps/2)-1)
    
    fig = Viewer.ax.get_figure()
    fig.savefig(r'docs/Tutorials/View3D/CenterMiddel.png',format='png',dpi=300)
    
    #  Change programatically to the next plane
    Viewer.setPlane(int(zSteps/2))
    fig2 = Viewer.ax.get_figure()
    fig2.savefig(r'docs/Tutorials/View3D/CenterAboveMiddel.png',format='png',dpi=300)
    
    
    # Instead of only stepping through the data with the Qx and Qy in the plane
    # one can flip the view by clicking 0, 1, or 2 in the interactive view,
    # or do it programmatically by
    
    Viewer.changeAxis(0)
    xSteps = Viewer.X.shape[-1]

    # Notice that the shape of X, Y, and Z changes when the axis is flipped! 
    # The last dimension is alway 'orthogonal' to the view.
    Viewer.setPlane(int(xSteps/2)-1)
    
    fig3 = Viewer.ax.get_figure()
    fig3.savefig(r'docs/Tutorials/View3D/CenterQx.png',format='png',dpi=300)

    # data from 3D Viewer can be saved as a mat file. The generated files are large, in the order of several GB.
    if False:
        savedata = {'data':V.Data, 'bins':V.bins}
        savemat("matlab_matrix.mat", savedata)         
    

    
    
    
    
title = 'Viewer 3D'

introText = 'In a single crystal experiment, the first step is to gain an overview of the system. This is most often done '\
+'by performing an A3 scan with the sample in a specific scattering plane. Due to the 2D detector of DMC, such an A3 scan produces '\
+'a 3D set of measured data points. In the frame of reference of the instrument, the majority of the covered volume is '\
+'in the Qx-Qy plane, i.e. with Qz close to zero. A single A3 slices corresponds to a curved line in th Qx-Qy '\
+' together with a symmetrically curved line in Qz. This sheet is then rotated around the origin with each A3 step.'\
+' Without an UB matrix, we can first look at the data in Q-space. This is done by having rlu=False.'\
+'\n\n'\
+'Interactivity\n'+'-'*len('Interactivity')+'\n'\
+'The Viewer 3D is an interactive plotting function which allows a look through the data in steps along the three major axes. '\
+'In the current build, these are along Qx, Qy, and Qz, and once can change between them by clicking keys on the keyboard '\
+'as tabulated below\n\n'\
+'+-----------------+------------------------------------------------------+ \n'\
+'|    Key press    | Effect                                               | \n'\
+'+-----------------+------------------------------------------------------+ \n'\
+'|        0        | Change plotting such that Qx is constant             | \n'\
+'+-----------------+------------------------------------------------------+ \n'\
+'|        1        | Change plotting such that Qy is constant             | \n'\
+'+-----------------+------------------------------------------------------+ \n'\
+'|        2        | Change plotting such that Qz is constant             | \n'\
+'+-----------------+------------------------------------------------------+ \n'\
+'| \+ or UpArrow   | Increment step along constant axis                   | \n'\
+'+-----------------+------------------------------------------------------+ \n'\
+'|  Page Up        | Increment 10 steps along constant axis               | \n'\
+'+-----------------+------------------------------------------------------+ \n'\
+'|\- or DownArrow  | Decrement step along constant axis                   | \n'\
+'+-----------------+------------------------------------------------------+ \n'\
+'|  Page Down      | Decrement 10 steps along constant axis               | \n'\
+'+-----------------+------------------------------------------------------+ \n'\
+'|        s        | Save current figure                                  | \n'\
+'+-----------------+------------------------------------------------------+ \n'\
+'|       End       | Skip to the end of allowed stop in this projection   | \n'\
+'+-----------------+------------------------------------------------------+ \n'\
+'|       Home      | Skip to the start of allowed stop in this projection | \n'\
+'+-----------------+------------------------------------------------------+ \n'\


outroText = 'The above code takes the data from a A3 scan '\
+'and generates the Viewer 3D utilizing a voxel size of 0.01 x 0.01 x 0.01 A:math:`^{-3}`. '\
+'By default, the viewer starts out in projection 2, i.e. with Qz being the axis stepped through. When handling the '\
+'data directly it is more convenient to utilize the keyboard shortcuts but in a scripting interface these are not '\
+'available. Instead one can utilize the *.setPlane* and *.changeAxis* methods. In addition, the color scale has been tweaked '\
+'such that weaker peaks are visible. It is possible to slightly tweak the color scale directly in the Viewer 3D by using the '\
+'sliders to the right of the color bar. Notice: When saving the figure these slides are rendered invisible. The end results are shown below:'\
+'\n\nFirst data overview with Qz slightly positive and Qx and Qy in the plane\n'\
+'\n.. figure:: CenterMiddel.png \n  :width: 50%\n  :align: center\n\n '\
+'\n\nOne step \'higher\' up along Qz in the same scattering plane\n'\
+'\n.. figure:: CenterAboveMiddel.png \n  :width: 50%\n  :align: center\n\n '\
+'\n\nFlipping of the scattering plane axis to 0, i.e. with Qx being constant\n'\
+'\n.. figure:: CenterQx.png \n  :width: 50%\n  :align: center\n\n '


introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('Viewer3D',introText,outroText,Tester,fileLocation = os.path.join(os.getcwd(),r'docs/Tutorials/View3D'))

def test_Viewer3D():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()