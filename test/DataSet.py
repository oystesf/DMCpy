from DMCpy import DataSet
from DMCpy import DataFile

def test_init():
    ds = DataSet.DataSet()

    assert(len(ds)==0)

    df = DataFile.DataFile('DEBUG')

    ds2 = DataSet.DataSet([df])
    assert(len(ds2)==1)

    ds3 = DataSet.DataSet(dataFiles=df)

    print(ds3.__dict__)
    print(ds2.__dict__)

    assert(ds2==ds3)