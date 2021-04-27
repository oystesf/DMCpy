import os.path
import numpy as np
from DMCpy import _tools



def test_fileListGenerator():

    fileString = '10-12,15-21,23'

    folder = 'data'
    year = 2021
    fileList = _tools.fileListGenerator(fileString,folder=folder,year=year)

    expected = ['data\\dmc2021n000010.hdf', 'data\\dmc2021n000011.hdf', 'data\\dmc2021n000012.hdf', 'data\\dmc2021n000015.hdf', 'data\\dmc2021n000016.hdf', 'data\\dmc2021n000017.hdf', 'data\\dmc2021n000018.hdf', 'data\\dmc2021n000019.hdf', 'data\\dmc2021n000020.hdf', 'data\\dmc2021n000021.hdf', 'data\\dmc2021n000023.hdf']
    
    assert(np.all(expected==fileList))

    # Generate year and fileString containing data file numbers from fileList
    yearGenerated,fileStringGenerated = _tools.numberStringGenerator(fileList)

    assert(yearGenerated==year)
    assert(fileStringGenerated == fileString)
