# -*- coding: utf-8 -*-
# Author: Ahmad Darmawan
import scrapy
import time
import urlparse
import re

import csv

from scrapy.selector import Selector
from scrapy.http import HtmlResponse

from time import gmtime, strftime

class ResearchSpider(scrapy.Spider):
    name = "research"
    custom_settings = {
        'DEPTH_LIMIT': '3',
        'DOWNLOAD_DELAY': '5.0',
        'DOWNLOAD_TIMEOUT' : '40'
    }
    # allowed_domains = ['six.akademik.itb.ac.id']
    start_url = ''
    allowed_domain = []

    filename = 'result.csv'

    def start_requests(self):
        start = getattr(self, 'url', None)
        allow = getattr(self, 'allow', None)

        self.start_url = start

        self.allowed_domain.extend(self.getURLHost(self.start_url))
        if allow is not None:
            words = allow.split(',')
            self.allowed_domain.extend(words)
        
        yield scrapy.Request(url=self.start_url, callback=self.parse, meta={'referer': '', 'name': ''})

    def parse(self, response):
        with open(self.filename, 'a') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([response.url, response.meta['referer'], response.meta['name'].encode('ascii', 'ignore'), strftime("%Y-%m-%d %H:%M:%S", gmtime())])
    
        for apath in response.xpath('//a'):
            for href in apath.xpath('@href').extract():
                text = apath.xpath('text()').extract()
                if (len(text)) != 0:
                    name = text[0].strip()
                else:
                    name = 'A'
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
        check = False
        for s in self.allowed_domain:
            if s in url:
                check = check or True
        if not check:
            return False
        
        pattern = re.compile('\.(pdf|jpe?g|docx?|xlsx?|pptx?|png|gif)$', re.I)
        if re.search(pattern, url) is not None:
            return False

        pattern = re.compile('^[0-9]{1,3}$')
        if re.search(pattern, text) is not None:
            return False

        words = []
        url_words = re.split("[^a-zA-Z0-9']+", url)
        words.extend(url_words)
        text_words = re.split("[^a-zA-Z0-9']+", text)
        words.extend(text_words)
        words = [x.lower() for x in words]

        exclude_words = ['blog', 'news', 'berita', 'tag', 'event', 'admin', 'kategori', 'category', 'download', 'downloads']
        if len(set(exclude_words).intersection(words)) > 0:
            return False

        return True
