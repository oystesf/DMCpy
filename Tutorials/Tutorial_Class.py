#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 08:09:38 2019

@author: lass
"""
#import pytest

import inspect
import pytest,types
import re



import os,sys,numpy as np

def formatCode(text,indentChar = '   ', skipHeader=1):
    """Formater for raw code strings to doc string formation"""
    
    text= text.split('\n')[skipHeader:]
    
    newText = []
    newText.append('.. code-block:: python\n   :linenos:\n')
    figCounter = 0
    for line in text:
        if line[:8] == ' '*8: # Replace initial blank with >>>
            line = indentChar + line[8:]
        elif line[:4] == ' '*4:
            line = indentChar + line[4:]
        elif len(line)==0:
            line = indentChar
            
        if line.find('savefig') != -1: # code contains a save function
            startP = line.find('(')
            endP = line.find(')')
            line = line[:startP] + "('figure{}.png',format='png')".format(figCounter) + line[endP+1:]
            figCounter+=1


        if (line.find(os.path.sep)!=-1 or line.find(os.path.altsep)!=-1) and line.find('DMC')!=-1:
            matches = re.findall(r'(\/.*?\.[\w:]+)',line)
            for match in matches:
                match
                fileName = os.path.split(match)[-1]
                line = line.replace(match,os.path.join('Path','To','Data','Folder',fileName)).replace('C:','')
        
            
        newText.append(line)
            
    return '\n'.join(newText)

class Tutorial(object):
    def __init__(self,name,introText,outroText,code,fileLocation=None,dependentFiles = None):
        self.name = name
        self.introText = introText
        self.outroText = outroText
        self.code = code
        self.dependentFiles = dependentFiles
        if not fileLocation is None:
            if fileLocation[-1] != os.path.sep:
                fileLocation += os.path.sep
            self.fileLocation = os.path.join(fileLocation,self.name.replace(' ','_')+'.rst')
        else:
            self.fileLocation = fileLocation
        
    def test(self):
        # if sys.platform == 'win32':
        #     if sys.version_info.major == 3 and sys.version_info.minor <8: # replace on code objects is not supported
        #         raise NotImplementedError('Cannot run this on your current version of python. You have {} but python 3.8 or later is needed.'.format(sys.version))
        #     Tester = self.code

        #     consts = Tester.__code__.co_consts
        #     tempList = np.array(list(consts),dtype=object)
        #     returnList = []
        #     for item in tempList:
        #         try:
        #             if '/home/' in item:
        #                 if 'Software' in item:
        #                     item = item.replace('/home/lass/Dropbox/PhD/Software',r'C:/Users/lass_j/Documents/Software').replace('/','\\')
        #                 elif 'CAMEAData' in item:
        #                     item = item.replace('/home/lass/Dropbox/PhD/CAMEAData',r'C:/Users/lass_j/Documents/CAMEA2018').replace('/','\\')
        #         except:
        #             pass
        #         returnList.append(item)
        #
        #    Tester.__code__ = Tester.__code__.replace(co_consts=tuple(returnList))
        #    Tester()
        #else:
        self.code()
        
    def generateTutorial(self):

        if not self.dependentFiles is None:
            
            folder = os.path.sep.join(self.fileLocation.split(os.path.sep)[:-1])+os.path.sep
            print("Copying files to {}".format(folder))
            from shutil import copyfile
            for f in list(self.dependentFiles):
                copyfile(f, folder+f.split(os.path.sep)[-1])
        
        # Test if code is running
        codeLocation = inspect.getsourcefile(self.code)
        codeFunctionName = 'test_'+self.name.replace(' ','_')
        #print('pytest '+'{}::{}'.format(codeLocation,codeFunctionName))
        print('Running tests for "{}" in file "{}"'.format(codeFunctionName,codeLocation.split(os.path.sep)[-1]))
        result = pytest.main(args=['-q','{}::{}'.format(codeLocation,codeFunctionName)])
        
        if result != 0:
            return None
            #raise RuntimeError('An error occurred while running pytest for "{}" defined in function "{}"'.format(codeFunctionName,codeLocation))    
        else:
            print('Test successful!')

        #if sys.platform == 'win32':
        #    fileLocation = self.fileLocation.replace('/home/lass/Dropbox/PhD/Software',r'C:/Users/lass_j/Documents/Software').replace('/','\\')
        #else:
        fileLocation = self.fileLocation
        
        introText = self.introText
        outroText = self.outroText
        codeText = inspect.getsource(self.code)
        
        code = formatCode(codeText)
        
        
        text = introText + '\n\n' + code + '\n\n'+ outroText
        
        if fileLocation is None:
            print(text)
            
        else:
            print('Saving code example to "{}".'.format(fileLocation))
            with open(fileLocation,'w') as f:
                f.write(text)

            print('Saving to local file')
            with open(os.path.join('Tutorials','tutorialList.txt'),'a') as f:
                f.write(fileLocation+'\n')
            
