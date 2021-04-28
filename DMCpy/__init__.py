import sys,os
sys.path.append('.')
import pickle

__version__ = '0.1.4'
__author__ = 'Jakob Lass'

installFolder = os.path.abspath(os.path.split(__file__)[0])
pythonPath =  os.path.join(installFolder,'calibrationDict.dat')

try:
    with open(pythonPath,'rb') as f:
        calibrationDict = pickle.load(f)
except FileNotFoundError:
    print('Current folder is '+__file__)
    print("Contents of local folder is: {}".format(os.listdir(installFolder)))
    print('Content of parent folder is: {}'.format(os.listdir(os.path.join(installFolder,'..'))))
    print('Content of parent folder is: {}'.format(os.listdir(os.path.join(installFolder,'..','..'))))
    print('Content of parent folder is: {}'.format(os.listdir(os.path.join(installFolder,'..','..','..'))))
    print('Content of parent folder is: {}'.format(os.listdir(os.path.join(installFolder,'..','..','..','..'))))
    print('Content of parent folder is: {}'.format(os.listdir(os.path.join(installFolder,'..','..','..','..','..'))))
    print('Content of parent folder is: {}'.format(os.listdir(os.path.join(installFolder,'..','..','..','..','..','..'))))

    

    def find(name, path):
        result = []
        for root, dirs, files in os.walk(path):
            if name in files:
                result.append(os.path.join(root, name))
        return result

    print(find('calibrationDict.dat',os.path.abspath(os.path.join(installFolder,'..','..','..','..','..','..'))))
    raise FileNotFoundError