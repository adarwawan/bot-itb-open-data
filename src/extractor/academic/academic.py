"""
Template rule-based-extractor
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
import time
from time import gmtime, strftime
from manage_db import DBManager

class TemplateExtractor(object):
    def __init__(self, dirout, url, identity, template):
        self.dirout = dirout
        self.url = url
        json_data = open(template).read()
        self.data = json.loads(json_data)
        self.identity = identity 

    def getBody(self):
        accessed = False 
        while not accessed:
            try:
                page = urllib2.urlopen(self.url).read()
                accessed = True
                # page = open(self.url, 'r').read()
            except:
                time.sleep(3)
                None
        soup = BeautifulSoup(page, 'html.parser')
        return soup

    def getTemplate(self):
        return self.data
    
    def getCandidatesTemplate(self, body_soup, template):
        return self.printResultToJSON(body_soup.text, template)    

    def printResultToJSON(self, body_soup, template):
        result = {}
        for i in xrange(0,len(template['data'])):
            field = template['data'][i]['field_name']
            typ = template['data'][i]['type']
            pat = template['data'][i]['pattern']

            pat_re = re.compile(pat)
            temps = pat_re.findall(body_soup)
            
            if len(temps) > 0:
                if ((template['data'][i]['count']) == 'single'):
                    if ((template['data'][i].has_key('filter'))):
                        temps[0] = temps[0].strip()
                    result[field] = temps[0]
                else:
                    template_sec = template['data'][i]
                    result[field] = []
                    for temp in temps:
                        rtemp = self.printResultToJSON(temp, template_sec)
                        result[field].append(rtemp)
        return result

    def createFile(self, result):
        fout = 'test' + '.json'
        # out_path = self.dirout+ "0-" +fout
        out_path = "0-" +fout
        with open(out_path, 'w') as outfile:
            json.dump(result, outfile)
        return out_path

    def constructJSON(self, data):
        result = {}
        result['url'] = self.url
        result['identity'] = self.identity
        result['time'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        result['data'] = data        
    
        if len(result['data']) > 0:
            db = DBManager("academic")
            db.insertDoc(result)
            return 1

        return 0

def main(argv):
    if len(argv) != 2:
        print 'usage: python template_extractor.py <url> <template>'
        sys.exit(2)    
    
    output_dir = "clean_html/"
    filename = "test.html"
    sub_folder = os.path.splitext(basename(filename))[0] + "/"
    with open('crawl_result.txt', 'r') as myfile:
        urls = myfile.read().splitlines()

    count = 0
    i = 0
    for url in urls:
        print "("+ str(count) + "/" + str(i) + ") Collect data from: " + url
    	te = TemplateExtractor(output_dir+sub_folder, url, argv[0], argv[1])
    	body_soup = te.getBody()
    	template = te.getTemplate()
    	data = te.getCandidatesTemplate(body_soup, template)
        count += te.constructJSON(data)
        i += 1

    print("\n\n" + "JUMLAH URL YANG DIAKSES: " + str(len(urls)))
    print("JUMLAH DATA YANG MASUK KE DATABASE: " + str(count))

if __name__ == "__main__":
   main(sys.argv[1:])
