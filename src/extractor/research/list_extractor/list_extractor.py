"""
List rule-based-extractor
"""
from __future__ import division

import sys, getopt
from bs4 import BeautifulSoup
import codecs
import os, shutil
from os.path import basename
import json
import re
import urllib2, requests

class ListExtractor(object):
    def __init__(self, dirout, url):
        self.dirout = dirout
        self.url = url
        # self.body = body
        self.listCount = 0
        with open(self.dirout + 'positive.txt', 'r') as myfile:
            self.positive = myfile.readlines()
        self.clearFile(self.dirout + "result")
        body_soup = self.getBody()
        lists = self.getCandidatesUnorderedList(body_soup)
        lists = self.getCandidatesOrderedList(body_soup)

    def clearFile(self, dir3):
        for the_file in os.listdir(dir3):
            file_path = os.path.join(dir3, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    def getBody(self):
        s = requests.Session()
        s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
        r = s.get(self.url)
        soup = BeautifulSoup(r.content, 'html.parser')
        return soup

    def getCandidatesUnorderedList(self, body_soup):
        # TODO: add rules for cell length consistensy(?)
        isList = False
        list_element = body_soup.find_all('ul')
        counteri = len(list_element)
        headers = []
        for i in range(0,counteri):
            header = body_soup.find_all('ul')[i].find_previous(string=True)
            while (header.strip() == ''):
                header = header.find_previous(string=True)
            headers.append(header)
        lists = []
        if len(list_element) > 0:
            j = 0
            for l in list_element:
                child_list = l.find_all('ul')
                if len(child_list) == 0:
                    # ciri-ciri bibliografi?
                    # selection ul
                    if (self.wordAvgLimit(l) and self.relevantTitle(headers[j]) and self.hasPunctuation(l)):
                        isList = True
                    if isList:
                        # print(l)
                        out_path = self.printListToFile(l, headers, j, self.listCount)
                        lists.append(out_path)
                        self.listCount = self.listCount + 1
                        isList = False
                j += 1
        # print(lists)
        return 0

    def getCandidatesOrderedList(self, body_soup):
        # TODO: add rules for cell length consistensy(?)
        isList = False
        list_element = body_soup.find_all('ol')
        counteri = len(list_element)
        headers = []
        for i in range(0,counteri):
            header = body_soup.find_all('ol')[i].find_previous(string=True)
            while (header.strip() == ''):
                header = header.find_previous(string=True)
            headers.append(header)
        lists = []
        if len(list_element) > 0:
            j = 0
            for l in list_element:
                child_list = l.find_all('ol')
                if len(child_list) == 0:
                    # ciri-ciri bibliografi?
                    # selection ul
                    if (self.wordAvgLimit(l) and self.relevantTitle(headers[j]) and self.hasPunctuation(l)):
                        isList = True
                    if isList:
                        # print(l)
                        # print("BBBBB")
                        out_path = self.printListToFile(l, headers, j, self.listCount)
                        lists.append(out_path)
                        self.listCount = self.listCount + 1
                        isList = False
                j += 1
        # print(lists)
        return 0

    def wordAvgLimit(self, list_soup):
        threshold = 0.9 # dipikirin ya
        isPass = False
        list_element = list_soup.find_all('li')
        count = len(list_element) + 1
        total = 0
        for i in xrange(0,len(list_element)):
            words = re.split("[^a-zA-Z0-9']+", list_element[i].text)
            total = total + len(words)
        avg = total / count
        return (avg > threshold)

    def relevantTitle(self, header):
        for i in xrange(0,len(self.positive)):
            pattern = re.compile(self.positive[i].replace("\n", ""), re.I)
            if re.search(pattern, header) is not None:
                return True
        return False

    def printListToFile(self, list_soup, headers, j, counter):
        lines = list_soup.findAll('li') 
        fout = 'list' + '.txt'
        out_path = self.dirout + "result/" + str(counter)+"-"+fout
        
        with codecs.open(out_path, 'w+', encoding='utf-8') as outfile:
            for line in lines:
                outfile.write(line.get_text().strip() + '\n')
        return out_path

    def hasPunctuation(self, list_soup):
        threshold = 0.95 # dipikirin ya
        isPass = False
        list_element = list_soup.find_all('li')
        count = len(list_element)
        total = 0
        for i in xrange(0,len(list_element)):
            pattern = re.compile('[,.:]', re.I)
            if re.search(pattern, list_element[i].text) is not None:
                total = total + 1
        avg = total / count
        return (avg > threshold)

def main(argv):
    if len(argv) != 1:
        print 'usage: python list_extractor.py <url>'
        sys.exit(2)    
    
    output_dir = ""
    rbe = ListExtractor(output_dir, argv[0])

if __name__ == "__main__":
   main(sys.argv[1:])