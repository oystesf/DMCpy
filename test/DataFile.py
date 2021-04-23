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

    df = DataFile.DataFile(filePath=os.path.join('data','dmc2018n000401.hdf'))
    path,name = os.path.split(os.path.join('data','dmc2018n000401.hdf'))

    assert(df.folder == path)
    assert(df.fileName == name)


def test_copy(): # Test the ability to copy from one data file to another
    testDF = DataFile.DataFile(os.path.join('data','dmc2018n000401.hdf'))

    testDFDict = testDF.__dict__

    dfCopy = DataFile.DataFile(testDF) # Perform copy

    assert(dfCopy._debugging == False)

    assert(dfCopy==testDF)

def test_load():
    testDF = DataFile.DataFile(os.path.join('data','dmc2018n000401.hdf'))

    assert(testDF.twoTheta.shape == (400,1))
    assert(testDF.counts.shape == (400,1))
    assert(testDF.correctedTwoTheta.shape == (400,1))

    # If detector is assumed to be flat, twoTheta and correctedTwoTheta are the same
    assert(np.all(np.isclose(testDF.correctedTwoTheta,testDF.twoTheta,atol=1e-4)))

    testDF = DataFile.DataFile(os.path.join('data','dmc2018n000401 - Copy.hdf'))

    assert(testDF.twoTheta.shape == (400,100))
    assert(testDF.counts.shape == (400,100))
    assert(testDF.correctedTwoTheta.shape == (400,100))

    # If detector is assumed to be flat, twoTheta and correctedTwoTheta are the same
    

def test_plot():
    dataFile = os.path.join('data','dmc2018n{:06d}.hdf'.format(401))

    df = DataFile.DataFile(dataFile)
    fig,ax = plt.subplots()

    Ax = df.plotDetector()

    dataFile = os.path.join('data','dmc2018n{:06d} - Copy.hdf'.format(401))

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

    df = DataFile.DataFile(os.path.join('data','dmc2018n000401 - Copy.hdf'))

    df.generateMask(maxAngle=90) # No points are masked
    assert(np.all(df.mask==np.ones_like(df.counts,dtype=bool)))

    df.generateMask(maxAngle=-1) # All points are masked
    assert(np.all(df.mask==np.zeros_like(df.counts,dtype=bool)))

    df.generateMask(maxAngle=7) # All points are masked
    total = np.size(df.counts)
    maskTotal = np.sum(df.mask)
    assert(total>maskTotal)
