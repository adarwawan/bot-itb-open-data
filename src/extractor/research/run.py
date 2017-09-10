"""
List rule-based-extractor
"""
from __future__ import division

import sys, getopt
from bs4 import BeautifulSoup
import codecs
import os
from os.path import basename
import json
import re
import urllib2
import glob
import subprocess

class RunExtractor(object):
    def __init__(self, out, url):
        self.out = out
        self.url = url
        self.listCount = 0
        os.chdir(url)        
	for file in glob.glob("*"):
          p=subprocess.Popen(["ruby", "../../extractor.rb", file], stdout=subprocess.PIPE)                              
          output,error = p.communicate()
          print(output)
	os.chdir("../..")

output_dir1 = "list_extractor/result"
output_dir2 = "table_extractor/result"
r = RunExtractor('testing.txt', output_dir1)
r = RunExtractor('testing.txt', output_dir2)
