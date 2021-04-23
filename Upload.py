
import glob
import os


def getLatestWheel():
    list_of_files = glob.glob('dist/*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def extractVersionFromWheel(fileName=None):
    if fileName is None:
        fileName = getLatestWheel()
    latestVersion = fileName.split('-')[-1].replace('.tar.gz','')
    return latestVersion

def getVersionInSetup():
    with open('setup.py') as f:
        lines = f.readlines()
    for l in lines:
        if l.find("    version='")!=-1:
            version = l.split('=')[-1][1:-1]
            break

    return version


latestVersion = extractVersionFromWheel()
setupVersion = getVersionInSetup()
if latestVersion != setupVersion:
    os.system("python setup.py sdist")

wheel = getLatestWheel()
os.system("twine upload {} -r pypi".format(wheel))