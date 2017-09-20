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
from json import JSONDecoder
import re
import urllib2
import glob
import subprocess
import pymongo
from time import gmtime, strftime
from manage_db import DBManager
from pymongo import MongoClient
from table_extractor.table_extractor import TableExtractor
from list_extractor.list_extractor import ListExtractor

class RunExtractor(object):
    def __init__(self, out, url, link, identity):
        self.out = out
        self.url = url
        self.link = link
        self.identity = identity
        self.listCount = 0
        os.chdir(url)        
	for file in glob.glob("*"):
          p=subprocess.Popen(["ruby", "../../extractor.rb", file], stdout=subprocess.PIPE)                              
          output,error = p.communicate()
          with open("../../" + self.out, "a") as myfile:
            myfile.write(output)
	os.chdir("../..")

    def constructJSON(self):
        result = {}
        result['url'] = self.link
        result['identity'] = self.identity
        result['time'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        result['data'] = []
        with open(self.out, "r") as myfile:
            stringData = myfile.read().splitlines()
        
        if (len(stringData) != 0):
            for string in stringData:
                data = JSONDecoder().decode(string)
                if data is not None:
                    if ('-a' not in data['id']):
                        result['data'].append(data)
            
            if len(result['data']) != 0:
                db = DBManager("research")
                db.insertDoc(result)
                return 1

        return 0

def main(argv):
    if len(argv) != 1:
        print 'usage: python research.py <identity>'
        sys.exit(2)    
    
    with open('crawl_result.txt', 'r') as myfile:
        urls = myfile.read().splitlines()

    output_dir1 = "list_extractor/"
    output_dir2 = "table_extractor/"

    result = "result/"
    
    count = 0
    i = 0
    for url in urls:
        print "("+ str(count) + "/" + str(i) + ") Collect data from: " + url
        rbe = ListExtractor(output_dir1, url)
        rbe = TableExtractor(output_dir2, url)

        f1 = open('testing.txt', 'w')

        r = RunExtractor('testing.txt', output_dir1 + result, url, argv[0])
        r = RunExtractor('testing.txt', output_dir2 + result, url, argv[0])
        count += r.constructJSON()
        i += 1

    print("\n\n" + "JUMLAH URL YANG DIAKSES: " + str(len(urls)))
    print("JUMLAH DATA YANG MASUK KE DATABASE: " + str(count))

if __name__ == "__main__":
   main(sys.argv[1:])