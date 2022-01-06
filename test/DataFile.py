from DMCpy import DataFile
import os.path
import numpy as np
import matplotlib.pyplot as plt

def test_init():
    df = DataFile.DataFile()

    try:
        df = DataFile.DataFile(r'Wrong\Path') # File not found
        assert False
    except FileNotFoundError:
        assert True

    testDF = DataFile.DataFile('DEBUG')
    assert(testDF._debugging == True)

    df = DataFile.DataFile(file=os.path.join('data','dmc2021n000494.hdf'))
    path,name = os.path.split(os.path.join('data','dmc2021n000494.hdf'))

    assert(df.folder == path)
    assert(df.fileName == name)


def test_copy(): # Test the ability to copy from one data file to another
    testDF = DataFile.DataFile(os.path.join('data','dmc2021n000494.hdf'))

    testDFDict = testDF.__dict__

    dfCopy = DataFile.DataFile(testDF) # Perform copy

    assert(dfCopy._debugging == False)

    assert(dfCopy==testDF)

def test_load():
    testDF = DataFile.DataFile(os.path.join('data','dmc2021n000494.hdf'))

    assert(testDF.twoTheta.shape == (128,128*9))
    assert(testDF.counts.shape == (1,128,128*9))
    assert(testDF.correctedTwoTheta.shape == (1,128,128*9))

    # If detector is assumed to be flat, twoTheta and correctedTwoTheta are the same at middle
    
    assert(np.all(np.isclose(np.mean(testDF.correctedTwoTheta[0,[63,64],:],axis=0),testDF.twoTheta[63,:],atol=0.06)))

    #testDF = DataFile.DataFile(os.path.join('data','dmc2018n000401 - Copy.hdf'))

    #assert(testDF.twoTheta.shape == (400,100))
    #assert(testDF.counts.shape == (400,100))
    #assert(testDF.correctedTwoTheta.shape == (400,100))

    # If detector is assumed to be flat, twoTheta and correctedTwoTheta are the same
    

def test_plot():
    dataFile = os.path.join('data','dmc2021n{:06d}.hdf'.format(494))

    df = DataFile.DataFile(dataFile)
    fig,ax = plt.subplots()

    Ax = df.plotDetector()


def test_masking_2D():
    df = DataFile.DataFile()

    # An empty data file raises error on making a mask
    try:
        df.generateMask()
        assert False
    except RuntimeError:
        assert True

    df = DataFile.DataFile(os.path.join('data','dmc2021n{:06d}.hdf'.format(494)))

    df.generateMask(maxAngle=90) # No points are masked
    assert(np.all(df.mask==np.zeros_like(df.counts,dtype=bool)))

    df.generateMask(maxAngle=-1) # All points are masked
    assert(np.all(df.mask==np.ones_like(df.counts,dtype=bool)))

    df.generateMask(maxAngle=7) # All points are masked
    total = np.size(df.counts)
    maskTotal = np.sum(np.logical_not(df.mask))
    assert(total>maskTotal)

    try:
        df.generateMask(MaxAngle=7)
        assert(False)
    except AttributeError as e:
        assert(e.args[0] == 'Key-word argument "MaxAngle" not understood. Did you mean "maxAngle"?')

    try:
        ax = df.plotDetector(aplynormalization=True)
        assert(False)
    except AttributeError as e:
        assert(e.args[0] == 'Key-word argument "aplynormalization" not understood. Did you mean "applyNormalization"?')
        


def test_calibration():
    fileName = 'dmc2018n000250.hdf' # no calibration exists

    calibData,calibName = DataFile.findCalibration(fileName)
    assert(calibName == 'None')
    assert(calibData is None)

    fileName = 'dmc2018n036099.hdf' # calibration deteff_18c.dat

    calibData,calibName = DataFile.findCalibration(fileName)
    assert(calibName == 'deteff_18c.dat')
    assert(calibData.shape == (400,))

    # Test when full data file path is provided
    fileName = os.path.join("fictive","folder","to","data",'dmc2002n000099.hdf') # calibration deteff_02c.dat
    calibData,calibName = DataFile.findCalibration(fileName)
    assert(calibName == 'deteff_02c.dat')
    assert(calibData.shape == (400,))

    # year not covered in calibration data
    fileName = 'dmc2019n000250.hdf'
    try:
        calibData,calibName = DataFile.findCalibration(fileName)
        assert(False)
    except FileNotFoundError:
        assert True


def test_decoding():
    dataFile = os.path.join('data','dmc2021n{:06d}.hdf'.format(494))

    df = DataFile.DataFile(dataFile)

    assert(isinstance(df.sample.name,str)) # Originally byte array
    

def test_saveLoad():
    dataFile = os.path.join('data','dmc2021n{:06d}.hdf'.format(494))
    df = DataFile.DataFile(dataFile)

    splitted = dataFile.split('.')
    splitted[-2] = splitted[-2] +'new'
    saveFileName = '.'.join(splitted)


    if os.path.exists(saveFileName):
        os.remove(saveFileName)
        
    df.save(saveFileName)
    df2 = DataFile.DataFile(saveFileName)
    assert(df==df)
    assert(df==df2)

    if os.path.exists(saveFileName):
        os.remove(saveFileName)


def test_changeOfParameters():
    dataFile = os.path.join('data','dmc2021n{:06d}.hdf'.format(494))
    df = DataFile.DataFile(dataFile,twoThetaPosition=np.array([1])) # Move the two theta position away from absolute 0

    originalKi = df.Ki
    originalWaveLength = df.waveLength
    originalQ = df.q

    df.Ki = 2.0
    assert(np.isclose(df.waveLength,np.pi))
    assert(np.all(np.logical_not(np.isclose(df.q,originalQ))))

    df.waveLength = 2.0
    assert(np.isclose(df.Ki,np.pi))
    assert(np.all(np.logical_not(np.isclose(df.q,originalQ))))
    
    df.Ki = originalKi
    assert(np.isclose(df.waveLength,originalWaveLength))
    assert(np.all(np.isclose(df.q,originalQ)))

    df2 = DataFile.DataFile(dataFile)
    df2.twoThetaPosition = np.array([1])
    assert(df==df2)


    splitted = dataFile.split('.')
    splitted[-2] = splitted[-2] +'new'
    saveFileName = '.'.join(splitted)
    if os.path.exists(saveFileName):
        os.remove(saveFileName)
        
    ## Change all parameters and save to check reproducibility
    df.Ki = 2
    df.twoThetaPosition = np.array([20.0])
    
    df.save(saveFileName)
    df2 = DataFile.DataFile(saveFileName)
    assert(df==df2)

    if os.path.exists(saveFileName):
        os.remove(saveFileName)
    
