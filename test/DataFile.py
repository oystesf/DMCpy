from DMCpy import DataFile


def test_init():
    df = DataFile.DataFile()

    try:
        df = DataFile.DataFile(r'Wrong\Path') # File not found
        assert False
    except FileNotFoundError:
        assert True

    testDF = DataFile.DataFile('DEBUG')
    assert(testDF._debugging == True)

    df = DataFile.DataFile(filePath=__file__) # load self as file - only temporary check
    import os.path
    path,name = os.path.split(__file__)

    assert(df.folder == path)
    assert(df.fileName == name)


def test_copy(): # Test the ability to copy from one data file to another
    testDF = DataFile.DataFile('DEBUG')

    testDFDict = testDF.__dict__

    dfCopy = DataFile.DataFile(testDF) # Perform copy

    assert(dfCopy._debugging == True)

    assert(dfCopy==testDF)