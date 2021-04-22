from DMCpy import DataSet
from DMCpy import DataFile
import os.path
import matplotlib.pyplot as plt

def test_init():
    ds = DataSet.DataSet()

    assert(len(ds)==0)

    df = DataFile.DataFile(os.path.join('data','dmc2018n{:06d}.hdf'.format(402)))

    ds2 = DataSet.DataSet([df])
    assert(len(ds2)==1)

    ds3 = DataSet.DataSet(dataFiles=df)

    print(ds3.__dict__)
    print(ds2.__dict__)

    assert(ds2==ds3)


def test_load():

    fileNumbers = range(401,411)
    dataFiles = [os.path.join('data','dmc2018n{:06d}.hdf'.format(no)) for no in fileNumbers]

    ds = DataSet.DataSet(dataFiles)
    
    assert(len(ds) == len(dataFiles))
    assert(ds[0].fileName == os.path.split(dataFiles[0])[-1])


    # load single file and check that it is equal to the corresponding file in ds
    ds2 = DataSet.DataSet(dataFiles[-1])
    assert(len(ds2) == 1)
    assert(ds2[0].fileName == os.path.split(dataFiles[-1])[-1])
    assert(ds2[0] == ds[-1])


def test_plot():

    fileNumbers = range(401,411)
    dataFiles = [os.path.join('data','dmc2018n{:06d}.hdf'.format(no)) for no in fileNumbers]


    ds = DataSet.DataSet(dataFiles)
    fig,ax = plt.subplots()

    Ax = ds.plotTwoTheta()
