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


output_dir = "clean_html/test"
r = RunExtractor('testing.txt', output_dir)
