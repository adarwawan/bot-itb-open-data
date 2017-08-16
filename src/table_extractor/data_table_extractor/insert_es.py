import requests
import csv
from collections import namedtuple
from elasticsearch import Elasticsearch

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

es = Elasticsearch()
reader = unicode_csv_reader(open('E:\\Dropbox\\[8]\\[cin]TA\\geonames\\ID.txt'), delimiter="\t", quoting=csv.QUOTE_MINIMAL)
current_nums = requests.get('http://localhost:9200/gaz-single-2/_count').json()['count']
print current_nums
i = 1
for row in reader:
    if i%1000 == 0:
    	print i
    if i > current_nums:
	    names = row[1] + ", " + row[2] + ", " + row[3]
	    place = {"geonameid" : row[0], "names" : names}
	    res = es.index(index='gaz-single-2', doc_type='toponym-single', id=row[0], body=place)
    i = i + 1
