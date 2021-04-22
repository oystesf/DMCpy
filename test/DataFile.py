from DMCpy import DataFile
import os.path
import numpy as np

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

