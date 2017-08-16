#This script will traverse through a directory and output a file as a result for concatenate all files on the dir

import sys
import os
import glob
from os.path import basename
from os.path import isfile
from os.path import abspath

path = "E:\\Dropbox\\[8]\\[cin]TA\\RawData\\mallet_trials\\3\\bps_train\\noyear\\"
outfile = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\crf_learner\\100_instances_new.txt"

os.chdir(path)

with open(outfile, "wb") as out:
	for file in glob.glob("*.txt"):
		with open(file, "rb") as infile:
			out.write(infile.read())
			out.write("\n")
