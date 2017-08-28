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

class ListExtractor(object):
    def __init__(self, dirout, url):
        self.dirout = dirout
        self.url = url
        self.listCount = 0
        with open('positive.txt', 'r') as myfile:
            self.positive = myfile.readlines()

    def getBody(self):
        page = urllib2.urlopen(self.url).read()
        soup = BeautifulSoup(page, 'html.parser')
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
                        print(l)
                        out_path = self.printListToFile(l, headers, j, self.listCount)
                        lists.append(out_path)
                        self.listCount = self.listCount + 1
                        isList = False
                j += 1
        print(lists)
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
                        print(l)
                        print("BBBBB")
                        out_path = self.printListToFile(l, headers, j, self.listCount)
                        lists.append(out_path)
                        self.listCount = self.listCount + 1
                        isList = False
                j += 1
        print(lists)
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
        fout = 'test' + '.txt'
        out_path = self.dirout + str(counter)+"-"+fout
        for line in lines:
            with codecs.open(out_path, 'a+', encoding='utf-8') as outfile:
                outfile.write(line.get_text() + '\n')
        return out_path

    def printCleanList(self, list_soup, headers, j, counter):
        pass

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
    
    output_dir = "clean_html/"
    filename = "test.html"
    sub_folder = os.path.splitext(basename(filename))[0] + "/"
    print sub_folder
    os.mkdir(output_dir+sub_folder)
    rbe = ListExtractor(output_dir+sub_folder, argv[0])
    body_soup = rbe.getBody()
    lists = rbe.getCandidatesUnorderedList(body_soup)
    lists = rbe.getCandidatesOrderedList(body_soup)

if __name__ == "__main__":
   main(sys.argv[1:])