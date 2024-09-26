import  os
# sys.path.append(r'C:\Users\lass_j\Documents\Software\DMCpy')
from Tutorial_Class import Tutorial


def Tester():
    from DMCpy import DataSet,DataFile,_tools
    import numpy as np
    import pickle


    # name for exports
    planeFigName = r'sample'

    # Give file number and folder the file is stored in.
    scanNumbers = '8540'
    folder = r'data\SC'
    year = 2022

    filePath = _tools.fileListGenerator(scanNumbers,folder,year=year)

    # # # load dataFiles
    dataFiles = [DataFile.loadDataFile(dFP) for dFP in filePath]

    # load data files and make data set
    ds = DataSet.DataSet(dataFiles)

    # use InteractiveViewer to find conditions for integration
    if False:
        IA1 = ds[0].InteractiveViewer()
        IA1.set_clim(0,20)
        IA1.set_clim_zIntegrated(0,1000)


    peakDict = { }

    # stor integration parameters in peakDict
    peakDict['111'] = {
                    'h' : 1,
                    'k' : 1,
                    'l' : 1,
                    'df' : 0,
                    'A3_center' : 113.57,
                    'A3_minus' : 10,
                    'A3_pluss' : 10,
                    'tth' : 49.5,
                    'tth_minus' : 2.1,
                    'tth_pluss' : 2.5,
                    'startZ' : 35,
                    'stopZ' : 100,
                    'vmin' : 0,
                    'vmax' : 0.005,
                }
    
    # add more peaks to the peakDict
    peakDict['110'] = {
                    'h' : 1,
                    'k' : 1,
                    'l' : 0,
                    'df' : 0,
                    'A3_center' : 78.5,
                    'A3_minus' : 10,
                    'A3_pluss' : 10,
                    'tth' : 36.2,
                    'tth_minus' : 2.1,
                    'tth_pluss' : 2.5,
                    'startZ' : 35,
                    'stopZ' : 85,
                    'vmin' : 0,
                    'vmax' : 0.005,
                }

    # to integrate all peaks in peakDict
    integrationList = None

    # to integrate only one or a list of peak, list the peaks you want to integrate in integrationList 
    integrationList = ['111']

    # keywords for box integration
    integrationKwargs = {
    'roi' : True,
    'saveFig' : r'docs/Tutorials/box/box1_',
    'title' : r'CeBr$_3$',
    'integrationList' : integrationList,
    'closeFigures' : True,
    'plane' : 'HHL'
    }

    integratedPeakDict = ds.boxIntegration(peakDict,**integrationKwargs)

    # print information
    if False:
        for peak in integratedPeakDict:
            print(integratedPeakDict[peak]['fit'][1])


    # Make hkl file
    if False:
        # Specify the file name
        file_name = f"docs/Tutorials/box/{planeFigName}.hkl"

        # Open the file in write mode
        with open(file_name, 'w') as file:
            # Write the column headers with appropriate spacing
            file.write('{:>3} {:>3} {:>3} {:>10} {:>10}\n'.format('h', 'k', 'l', 'Int', 'err'))

            # Loop through the peaks in integratedPeakDict and write the data
            for peak in integratedPeakDict:
                # Format the data with consistent spacing, considering the negative sign
                h = int(integratedPeakDict[peak]['h'])
                k = int(integratedPeakDict[peak]['k'])
                l = int(integratedPeakDict[peak]['l'])
                intensity = np.round(integratedPeakDict[peak]['summed_counts'], 4)
                error = np.round(np.sqrt(integratedPeakDict[peak]['summed_counts'] * np.mean(integratedPeakDict[peak]['monitors'])) / np.mean(integratedPeakDict[peak]['monitors']), 4)

                # Use a modified format string to align numbers to the right
                peak_data = '{:>3} {:>3} {:>3} {:>10} {:>10}\n'.format(h, k, l, intensity, error)

                # Write the formatted data to the file
                file.write(peak_data)

        print(f"Data has been written to {file_name}")


    # save dictionary
    if False:
        file_name = f"docs/Tutorials/box/{planeFigName}.pickle"
        with open(file_name, 'wb') as file:
            pickle.dump(integratedPeakDict, file)
        print(f"Data has been written to {file_name}")

        # load dictionary
        if False:
            # Load dictionary from file
            file_name = f"docs/Tutorials/box/{planeFigName}.pickle"
            with open(file_name, 'rb') as file:
                loaded_dict = pickle.load(file)

            print(loaded_dict)


    # export xy data
    if False:
        file_name = f"docs/Tutorials/box/{planeFigName}.txt"
        with open(file_name, 'w') as file:
            for key, values in integratedPeakDict.items():
                # print(key)
                file.write(f'{key}' + '\n')
                file.write(' '.join(map(str, values['peak_cut'][0])) + '\n')
                file.write(' '.join(map(str, values['peak_cut'][1])) + '\n')
                file.write(' '.join(map(str, values['monitors'])) + '\n')
                file.write('\n')  # Add a new line to separate data sets

        print(f"Data has been written to {file_name}")

        
    
    
    
title = 'Box integration'

introText = 'This tutorial demonstrate a primitive method for integrating Bragg peaks from single crystals. '\
+'Here, we define a range in A3 and 2Theta, and sum the intensities in the region. This means that the detector operates as a point detector. '\
+'We can plot the integrated intensities and fit it with a Gaussian peak. '\
+'You shoud use InteractiveViewer and View3D to determin the correct integration parameters, in addition to inspecting the roi. '\
+'Note that when you use several dataFiles in one dataSet, you must give the dataFile index in the peakDict. '\



outroText = 'The above code takes the data from the A3 scan file dmc2022n008540, and select and area in A3 and pixels. '\
+'It then sums the detector in the given pixel area and extract the intensity as a function of A3. '\
+'The integration details are given in a dictionary. The A3 range is given in frames, while the tth range is in degrees. '\
+'startZ and stopZ gives the height on the detector in pixels (0-128). The roi keyword determines if the rois are plotted. '\
+'\n\nIntensity as a function of A3 \n'\
+'\n.. figure:: box1_111.png \n  :width: 50%\n  :align: center\n\n '\
+'\n\nVisualization of the pixel area of the detector used \n'\
+'\n.. figure:: box1_111_roi.png \n  :width: 50%\n  :align: center\n\n '\

introText = title+'\n'+'^'*len(title)+'\n'+introText


    
Example = Tutorial('box',introText,outroText,Tester,fileLocation = os.path.join(os.getcwd(),r'docs/Tutorials/box'))

def test_box():
    Example.test()

if __name__ == '__main__':
    Example.generateTutorial()