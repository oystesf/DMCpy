from DMCpy import DataSet
from DMCpy import DataFile
import os.path
import matplotlib.pyplot as plt
import numpy as np

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

    # Find length before appending
    length = len(ds)
    ds.append(dataFiles)

    # Length is supposed to be both
    assert(len(ds)==length+len(dataFiles))

    # Also works for adding data files directly (both in list and as object)
    df = ds2[0]
    ds.append([df])
    assert(len(ds)==length+len(dataFiles)+1)
    ds.append(df)
    assert(len(ds)==length+len(dataFiles)+2)

    # Deletion
    del ds[-1]
    assert(len(ds)==length+len(dataFiles)+1)

def test_plot():

    fileNumbers = range(401,411)
    dataFiles = [os.path.join('data','dmc2018n{:06d}.hdf'.format(no)) for no in fileNumbers]


    ds = DataSet.DataSet(dataFiles)
    fig,ax = plt.subplots()

    Ax, bins, intensity, error, monitor = ds.plotTwoTheta()

    Ax,*_ = ds.plotTwoTheta(correctedTwoTheta=False)

    # Calculate bins, intensity, error without plotting

    bins2, intensity2, error2, monitor2 = ds.sumDetector()

    assert(np.all(np.isclose(bins,bins2)))
    assert(np.all(np.isclose(intensity,intensity2)))
    assert(np.all(np.isclose(error,error2)))
    assert(np.all(np.isclose(monitor,monitor2)))
    

def test_2d():
    fileNumbers = range(401,411)
    dataFiles = [os.path.join('data','dmc2018n{:06d} - Copy.hdf'.format(no)) for no in fileNumbers]

    ds = DataSet.DataSet(dataFiles=dataFiles)

    files = len(fileNumbers)
    assert(ds.counts.shape == (files,400,100))

    ax1 = ds.plotTwoTheta(correctedTwoTheta=False)
    ax2 = ds.plotTwoTheta(correctedTwoTheta=True)


def test_kwargs():
    
    fileNumbers = range(401,402)
    dataFiles = [os.path.join('data','dmc2018n{:06d} - Copy.hdf'.format(no)) for no in fileNumbers]

    ds = DataSet.DataSet(dataFiles=dataFiles)

    try:
        _ = ds.sumDetector(corrected=False)
        assert(False)
    except AttributeError as e:
        assert(e.args[0] == 'Key-word argument "corrected" not understood. Did you mean "correctedTwoTheta"?')

    ds = DataSet.DataSet(dataFiles=dataFiles)

    try:
        _ = ds.plotTwoTheta(corrected=False,fmt='.-')
        assert(False)
    except AttributeError as e:
        assert(e.args[0] == 'Key-word argument "corrected" not understood. Did you mean "correctedTwoTheta"?')

    