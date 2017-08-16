import sys
import os
from shutil import copyfile
from os.path import basename
from os.path import isfile
from os.path import abspath

path = "E:\\Dropbox\\[8]\\[cin]TA\\RawData\\downloaded\\train_tables3\\"
listOfFiles = []

for file in os.listdir(path):
	current = os.path.join(path, file)
	if (isfile(current)):
		currentfilename = basename(current) + "\n"
		listOfFiles.append(currentfilename)
