"""
feature_extractor
"""

from __future__ import division
import sys
from bs4 import BeautifulSoup
import codecs
import re
from math import log, floor
import os
from os.path import basename

class RowFeatureExtractor(object):
    def __init__(self, fin, dirout):
        self.fin = fin
        self.dirout = dirout
        self.features = []
        
    def getTable(self):
        soup = BeautifulSoup(open(self.fin), 'html.parser')
        return soup.table
    
    def setArrayOfAttr(self, row_soup):
        """ To be done for each row on a table. """
        cells = row_soup.find_all('td')
        cells = cells + row_soup.find_all('th')
        isMerged = self.fillIsMerged(cells)
        isHead = self.fillIsHead(cells)
        (isEmpty, isShortText, isLongText, isNumeric, isYear) = self.fillContentAttr(cells)
        AisMerged = self.countA(isMerged)
        AisHead = self.countA(isHead)
        AisEmpty = self.countA(isEmpty)
        AisShortText = self.countA(isShortText)
        AisLongText = self.countA(isLongText)
        AisNumeric = self.countA(isNumeric)
        AisYear = self.countA(isYear)
        B = self.countB(cells)
        row_features = str(AisYear) + "," + str(AisMerged) + "," + str(AisHead) + "," + str(AisEmpty) + "," + str(AisShortText) + "," + str(AisLongText) + "," + str(AisNumeric) + "," + str(B) + "\n"
        self.features.append(row_features)
        return
    
    def countValInArray(self, arr, val):
        return len([a for a in arr if a==val])
    
    def isNumericString(self, str_in):
        pattern = "^((\d)+(\.|,| )*(\d)*)$"
        result = re.match(pattern, str_in)
        # print result
        if result == None:
            return False
        else:
            return True
    
    def isYearString(self, str_in):
        ret = False
        pattern = "^((\d)+)$"
        result = re.match(pattern, str_in)
        if result == None:
            pass
        else:
            if len(str_in) == 4:
                if int(str_in) >= 1700 and int(str_in) <= 2016:
                    ret = True
        return ret
    
    # The following methods require setArrayOfAttr to be done first
    def countB(self, cells):
        b = 0.0
#         cells = row_soup.find_all('td')
#         cells = cells + row_soup.find_all('th')
        if len(cells) > 0:
            b = floor(log(len(cells), 2))
        return b
    
    def fillIsMerged(self, cell_list):
        ret = []
        for c in cell_list:
            if self.hasAttr(c, 'colspan') or self.hasAttr(c, 'rowspan'):
                ret.append(1)
            else:
                ret.append(0)
        return ret
    
    def fillIsHead(self, cell_list):
        ret = []
        for c in cell_list:
            if c.name == 'th':
                ret.append(1)
            else:
                ret.append(0)
        return ret
    
    def fillContentAttr(self, cell_list):
        isEmpty = []
        isShortText = []
        isLongText = []
        isNumeric = []
        isYear = []
        for c in cell_list:
            if (not self.isCellHasImage(c) and not self.isCellHasText(c)):
                isEmpty.append(1)
                isShortText.append(0)
                isLongText.append(0)
                isNumeric.append(0)
                isYear.append(0)
            else:
                isEmpty.append(0)
                content = c.get_text().strip()
                if self.isNumericString(content):
                    if self.isYearString(content):
                        isYear.append(1)
                        isNumeric.append(0) #TODO: rethink, is it better like this or 'year is numeric' allowed
                    else:
                        isYear.append(0)
                        isNumeric.append(1)
                    isShortText.append(0)
                    isLongText.append(0)
                else:
                    isYear.append(0)
                    isNumeric.append(0)
                    if len(content) < 80: #TODO: rethink about the limit
                        isShortText.append(1)
                        isLongText.append(0)
                    else:
                        isShortText.append(0)
                        isLongText.append(1)
        return isEmpty, isShortText, isLongText, isNumeric, isYear
    
    # Require fillAllAttr to be done first
    def countA(self, attr_list): 
        a = 0.0
        c = float(self.countValInArray(attr_list, 1))
        r = float(len(attr_list))
        if c > 0 and c <= (r/2):
            a = floor(log(c, 2) + 1.0)
        elif c > (r/2) and c < r:
            a = floor(log((r-c), 2) + 1.0)
        else:
            pass
        return a
    
    def printFeaturesToFile(self):
        """ print list of feature per line (use writelines) """
        fname, ext = basename(self.fin).split('.')
        fout = os.path.join(self.dirout, fname + "-features.txt")
        with open(fout, 'w+') as outfile:
            outfile.writelines(self.features)
        return fout
    
    def processTable(self, table_soup):
        rows = table_soup.find_all('tr')
        for r in rows:
            self.setArrayOfAttr(r)
        featuresfile = self.printFeaturesToFile()
        return featuresfile        
    
    def hasAttr(self, soup, attr):
        ret = False
        try:
            if soup.attrs[attr]:
                ret = True
        except:
            pass
        return ret
    
    def isCellHasImage(self, cell_soup):
        ret = False
        if len(cell_soup.find_all('img')) > 0:
            ret = True
        return ret
    
    def isCellHasText(self, cell_soup): # TODO: kalau cellnya isi "\u00a0", empty nggak?
        ret = True
        if cell_soup.get_text().strip()=='':
            ret = False
        if cell_soup.get_text() == '\u00a0':
            ret = False
        return ret

# rfe = RowFeatureExtractor("1-13.html", "feature-1-13.txt")
# table_soup = rfe.getTable()
# rfe.processTable(table_soup)