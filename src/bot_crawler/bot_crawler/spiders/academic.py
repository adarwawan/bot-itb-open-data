# -*- coding: utf-8 -*-
import scrapy
import time
import urlparse
import re

import csv

from scrapy.selector import Selector
from scrapy.http import HtmlResponse

from time import gmtime, strftime

class AcademicSpider(scrapy.Spider):
    name = "academic"
    custom_settings = {
        'DEPTH_LIMIT': '3',
        'DOWNLOAD_DELAY': '5.0',
        'DOWNLOAD_TIMEOUT' : '40'
    }
    # allowed_domains = ['six.akademik.itb.ac.id']
    start_url = ''
    allowed_domain = []

    filename = 'result_academic2.csv'

    def start_requests(self):
        start = getattr(self, 'url', None)
        allow = getattr(self, 'allow', None)
        # self.pat = getattr(self, 'pat', None)

        self.start_url = start

        self.allowed_domain.extend(self.getURLHost(self.start_url))
        if allow is not None:
            words = allow.split(',')
            self.allowed_domain.extend(words)
        
        yield scrapy.Request(url=self.start_url, callback=self.parse, meta={'referer': '', 'name': ''})

    def parse(self, response):
        if 'text/html' in response.headers.getlist('Content-Type')[0]:
          with open(self.filename, 'a') as f:
              writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
              writer.writerow([response.url, response.meta['referer'], response.meta['name'].encode('ascii', 'ignore'), strftime("%Y-%m-%d %H:%M:%S", gmtime())])
      
          for apath in response.xpath('//a'):
              for href in apath.xpath('@href').extract():
                  text = apath.xpath('text()').extract()
                  if (len(text)) != 0:
                      name = text[0].strip()
                  else:
                      name = 'None'
                  url = urlparse.urljoin(response.url, href)
              
              if self.violation_check(url, name):
                  yield scrapy.Request(url, callback=self.parse, meta={'referer': response.url, 'name': name })
          
    def getURLFrontier(self):
        with open('frontier.txt', 'r') as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        return content

    def getURLHost(self, _url):
        url = urlparse.urlsplit(_url)
        return [url.netloc]

    def violation_check(self, url, text):
        # pattern = re.compile(self.pat, re.I)
        # if re.search(pattern, url) is not None:
        #     return True
        # return False
        return True
