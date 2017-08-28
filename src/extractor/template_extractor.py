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
from academic_db import DBAcademic

class TemplateExtractor(object):
    def __init__(self, dirout, url, template):
        self.dirout = dirout
        self.url = url
        json_data = open(template).read()
        self.data = json.loads(json_data) 

    def getBody(self):
        accessed = False 
        while not accessed:
            try:
                # page = urllib2.urlopen(self.url).read()
                accessed = True
                page = open(self.url, 'r').read()
            except:
                print("MAAF")
                time.sleep(5)
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
        print(result)
        return result

    def createFile(self, result):
        fout = 'test' + '.json'
        # out_path = self.dirout+ "0-" +fout
        out_path = "0-" +fout
        with open(out_path, 'w') as outfile:
            json.dump(result, outfile)
        return out_path

def main(argv):
    if len(argv) != 2:
        print 'usage: python template_extractor.py <url> <template>'
        sys.exit(2)    
    
    output_dir = "clean_html/"
    filename = "test.html"
    sub_folder = os.path.splitext(basename(filename))[0] + "/"
    print sub_folder
    # os.mkdir(output_dir+sub_folder)
    rbe = TemplateExtractor(output_dir+sub_folder, argv[0], argv[1])
    body_soup = rbe.getBody()
    template = rbe.getTemplate()
    result = rbe.getCandidatesTemplate(body_soup, template)
    result['url'] = argv[0]
    print(result)
    db = DBAcademic()
    db.insertDoc(result)
    
if __name__ == "__main__":
   main(sys.argv[1:])