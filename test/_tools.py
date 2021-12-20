import os.path
import numpy as np
from DMCpy import _tools



def test_fileListGenerator():

    fileString = '10-12,15-21,23'

    folder = 'data'
    year = 2021
    fileList = _tools.fileListGenerator(fileString,folder=folder,year=year)

    expected = [os.path.join('data',f) for f in ['dmc2021n000010.hdf', 'dmc2021n000011.hdf', 'dmc2021n000012.hdf', 'dmc2021n000015.hdf', 'dmc2021n000016.hdf', 'dmc2021n000017.hdf', 'dmc2021n000018.hdf', 'dmc2021n000019.hdf', 'dmc2021n000020.hdf', 'dmc2021n000021.hdf', 'dmc2021n000023.hdf']]  
    assert(np.all(expected==fileList))

    # Generate year and fileString containing data file numbers from fileList
    yearGenerated,fileStringGenerated = _tools.numberStringGenerator(fileList)

    assert(yearGenerated==year)
    assert(fileStringGenerated == fileString)


def test_roundPower():
    assert(_tools.roundPower(0.0,default=10) == 10) # Default is returnd at 0

    assert(_tools.roundPower(0.1) == 1)

    assert(_tools.roundPower(0.01) == 2)

    assert(_tools.roundPower(0.09) == 2)

    assert(_tools.roundPower(10.09) == -1)

    assert(_tools.roundPower(1.09) == 0)