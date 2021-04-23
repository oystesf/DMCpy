#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 10:31:10 2019

@author: lass
"""

import sys
import glob
import os

if len(sys.argv)==1:
	
	list_of_files = glob.glob('dist/*') # * means all if need specific format then *.csv
	latest_file = os.path.split(max(list_of_files, key=os.path.getctime))[-1]


	latestVersion = [int(x) for x in latest_file.split('-')[-1].replace('.tar.gz','').split('.')]

	latestVersion[-1]+=1
	version = '{}.{}.{}'.format(*latestVersion)
else:
	version = sys.argv[1]

print('Updating to version ',version)

# update to new version in setup.py
with open('setup.py') as f:
	lines = f.readlines()
	writeLines = ''
	for l in lines:
		if l.find("    version='")!=-1:
			l ="    version='"+version+"',\n"
		writeLines+=l
			
with open('setup.py','w') as f:
	f.write(writeLines)

with open('DMCpy/__init__.py') as f:
	lines = f.readlines()
	writeLines = ''
	for l in lines:
		if l.find("__version__ = ")!=-1:
			idx = l.find('__version__ = ')
			l = l[:idx] + "__version__ = '"+version+"'\n"
		writeLines+=l
        
with open('DMCpy/__init__.py','w') as f:
	f.write(writeLines)


with open('test/init.py') as f:
	lines = f.readlines()
	writeLines = ''
	for l in lines:
		if l.find("__version__")!=-1:
			idx = l.find('__version__==')
			l = l[:idx] + "__version__=='"+version+"')\n"
		writeLines+=l
        
with open('test/init.py','w') as f:
	f.write(writeLines)

os.system("git add DMCpy/__init__.py test/init.py setup.py")
os.system('git commit -m "Update to version {}"'.format(version))
os.system('git tag -a {} -m "{}"'.format(version,version))
