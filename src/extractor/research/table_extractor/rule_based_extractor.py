"""
Table rule-based-extractor
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
from cookielib import CookieJar
import requests

class RuleBasedExtractor(object):
    def __init__(self, dirout, url):
        self.dirout = dirout
        self.url = url
        self.tableCount = 0
        with open(self.dirout + 'positive.txt', 'r') as myfile:
            self.positive = myfile.read().splitlines() 

    def getBody(self):
        s = requests.Session()
        s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
        r = s.get(self.url)
        soup = BeautifulSoup(r.content, 'html.parser')
        return soup
    
    def getTitleInsideTable(self, body_soup):
        # Title maybe in first th or first tr
        titles = body_soup.find_all('th')
        if len(titles) > 0:
            i = 0
            title = ""
            while ((title == "") and (i < len(titles))):
                header = titles[i]
                title = header.find_all(string=True)
                title = " ".join(title).strip() 
                i += 1
            return title
        else:
            titles = body_soup.find_all('td')
            if len(titles) > 0:
                i = 0
                title = ""
                while ((title == "") and (i < len(titles))):
                    header = titles[i]
                    title = header.find_all(string=True)
                    title = " ".join(title).strip() 
                    i += 1
                return title
            else:
                return "None"

    def getTitleOutsideTable(self, body_soup):
        title = body_soup.find_previous(string=True)
        while (title.strip() == ''):
            title = title.find_previous(string=True)
        return title

    def getCandidatesTable(self, body_soup):
        # TODO: add rules for cell length consistensy(?)
        isTable = False
        table_element = body_soup.find_all('table')
        counteri = len(table_element)
        headers = []
        for i in range(0,counteri):
            titleInside = self.getTitleInsideTable(body_soup.find_all('table')[i])
            titleOutside = self.getTitleOutsideTable(body_soup.find_all('table')[i])
            header = titleInside + " " + titleOutside
            headers.append(header)
        tables = []
        if len(table_element) > 0:
            j = 0
            for t in table_element:
                child_table = t.find_all('table')
                if len(child_table) == 0:
                    if (self.countBlank(t) != (self.countTh(t) + self.countTd(t))):
                        if self.countNonEmptyRow(t) > 2:
                            if (self.cellRowRatio(t) and self.imgLimit(t) and self.formLimit(t) and self.linkLimit(t)):
                                if (self.relevantTitle(headers[j])):
                                    isTable = True
                    if isTable:
                        out_path = self.printTableToFile(t, headers, j, self.tableCount)
                        tables.append(out_path)
                        self.tableCount = self.tableCount + 1
                        isTable = False
                j += 1
        # print(tables)
        return 0

    def isCellHasImage(self, cell_soup):
        ret = False
        if len(cell_soup.find_all('img')) > 0:
            ret = True
        return ret
    
    def isCellHasText(self, cell_soup):
        ret = True
        if cell_soup.get_text().strip()=='':
            ret = False
        return ret
    
    def countBlank(self, table_soup):
        """
        count cells that don't have text (cells contain only image is EMPTY)
        """
        n_blank = 0
        #TODO: try soup.contents to check if cell is blank(no text, no img, nothing)
        cells = table_soup.find_all('td')
        headers = table_soup.find_all('th')
        blank_cells = [c for c in cells if (not self.isCellHasImage(c) and not self.isCellHasText(c))]
#         blank_cells2 = [c for c in blank_cells if ]
#         print blank_cells
        blank_headers = [h for h in headers if h.get_text().strip()=='']
        n_blank = n_blank + len(blank_cells)
        n_blank = n_blank + len(blank_headers)
        return n_blank
    
    def countTr(self, table_soup):
        tr = table_soup.find_all('tr')
        return len(tr)
    
    def countTh(self, table_soup):
        th = table_soup.find_all('th')
        return len(th)
    
    def countTd(self, table_soup):
        td = table_soup.find_all('td')
        return len(td)
    
    def countNonEmptyRow(self, table_soup):
        nNonEmpty = 0
        tr = table_soup.find_all('tr')
        for r in tr:
            if not self.isRowEmpty(r):
                nNonEmpty = nNonEmpty + 1
        return nNonEmpty
    
    def cellRowRatio(self, table_soup):
        threshold = 1.5 # TODO: rethink about the threshold
        ret = False
        ratio = (self.countTd(table_soup)+self.countTh(table_soup)) / self.countTr(table_soup)
        if ratio > threshold:
            ret = True
        return ret
    
    def imgLimit(self, table_soup):
        isPass = False
        nImg = len(table_soup.find_all('img'))
        nonBlankCells = (self.countTh(table_soup) + self.countTd(table_soup)) - self.countBlank(table_soup)
        if nImg < nonBlankCells:
            # TODO: rethink about this
            if nImg < self.countNonEmptyRow(table_soup):
                isPass = True
        return isPass
        
    def formLimit(self, table_soup):
        isPass = False
        nForm = len(table_soup.find_all('form'))
        nInput = len(table_soup.find_all('input'))
        nSelect = len(table_soup.find_all('select'))
        if (nForm + nInput + nSelect) < self.countNonEmptyRow(table_soup):
            isPass = True
        return isPass
    
    def linkLimit(self, table_soup):
        isPass = False
        nA = len(table_soup.find_all('a'))
        threshold = 0.5 # TODO: rethink about thins threshold
        linkPercentage = nA / (self.countTd(table_soup) + self.countTh(table_soup) - self.countBlank(table_soup))
        if (linkPercentage < threshold):
            isPass = True
        return isPass
        
    def probablyRelational(self, table_soup):
        isPass = False
        nonBlankCells = (self.countTh(table_soup) + self.countTd(table_soup)) - self.countBlank(table_soup)
        if self.countTr(table_soup) < nonBlankCells: # TODO: rethink about this condition, how if the diff is not significant?
            isPass = True
        return isPass
    
    def printTableToFile(self, table_soup, headers, j, counter):
        pretty = table_soup.prettify()
        pretty = headers[j] + pretty
        html_string = "<html><body>" + pretty + "</body></html>"
        soup = BeautifulSoup(html_string, "html.parser")
        fout = 'test' + '.html'
        out_path = self.dirout + "clean_html/test/" + str(counter)+"-"+fout
        with codecs.open(out_path, 'w+', encoding='utf-8') as outfile:
            outfile.write(soup.prettify())
        return out_path
        
    
    def blankCellRule(self, table_soup):
        ret = False
        blankRatio = self.countTd(table_soup) / self.countBlank(table_soup)
        if blankRatio < 0.2: # TODO: rethink about this threshold
            ret = True
        return ret
    
    def isRowEmpty(self, row_soup):
        ret = False
        ntd = len(row_soup.find_all('td'))
        nth = len(row_soup.find_all('th'))
        nblank = self.countBlank(row_soup)
        if (nblank == (ntd + nth)):
            ret = True
        return ret

    def wordAvgLimit(self, list_soup):
        threshold = 6 # dipikirin ya
        isPass = False
        list_element = list_soup.find_all('li')
        count = len(list_element)
        total = 0
        for i in xrange(0,len(list_element)):
            # print(list_element[i].text)
            words = re.split("[^a-zA-Z0-9']+", list_element[i].text)
            total = total + len(words)
        avg = total / (count+1)
        return (avg > threshold)

    def notContainNumberLimit(self, list_soup):
        threshold = 0.90
        list_element = list_soup.find_all('li')
        count = len(list_element)
        total = 0
        for i in xrange(0,len(list_element)):
            s = list_element[i].text
            if re.search('20[0-9]{2,2}', s) is None:
                total += 1
        th = (count - total) / (count * (1.0))
        # print(th)
        # print(threshold)
        return (th > threshold)

    def relevantTitle(self, header):
        for i in xrange(0,len(self.positive)):
            pattern = re.compile(self.positive[i], re.I)
            if re.search(pattern, header) is not None:
                return True
        return False
            
def main(argv):
    if len(argv) != 1:
        print 'usage: python rule_based_extractor.py <url>'
        sys.exit(2)    
    
    output_dir = "clean_html/"
    filename = "test.html"
    sub_folder = os.path.splitext(basename(filename))[0] + "/"
    print sub_folder
    os.mkdir(output_dir+sub_folder)
    rbe = RuleBasedExtractor(output_dir+sub_folder, argv[0])
    body_soup = rbe.getBody()
    tables = rbe.getCandidatesTable(body_soup)
    
if __name__ == "__main__":
   main(sys.argv[1:])
