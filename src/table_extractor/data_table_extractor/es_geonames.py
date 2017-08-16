import requests
import csv
from collections import namedtuple
from elasticsearch import Elasticsearch

# res = requests.get('http://localhost:9200')
# print(res.content)
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
SearchResult = namedtuple('SearchResult', ['name', 'score', 'asciiname', 'alternate', 'geonameid'], verbose=True)

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

def get_search_score(es_con, idx, phrase):
    """ Get the highest search score for phrase """
    # query_body = {"size": 1, "query": {"dis_max": {"queries": [{"match": {"name": phrase}}, {"match": {"asciiname": phrase}}]}}}
    # query_body2 = { \
    #     "size" : 1, \
    #     "query": { \
    #         "multi_match": { \
    #             "fields": ["name", "asciiname", "alternatenames"], \
    #             "query": phrase, \
    #             "fuzziness": "AUTO" \
    #             } \
    #         } \
    #     }
    query_body3 = { \
        "size" : 1, \
        "query": { \
            "multi_match": { \
                "fields": ["name", "asciiname", "alternatenames"], \
                "query": phrase, \
                "fuzziness": "AUTO", \
                "type" : "phrase" \
                } \
            } \
        }
    print phrase
    res = es_con.search(index=idx, body=query_body3)
    # print res['hits']['max_score']
    if len(res['hits']['hits']) > 0:
        sr = SearchResult(name=res['hits']['hits'][0]['_source']['name'], score=res['hits']['hits'][0]['_score'], \
            asciiname=res['hits']['hits'][0]['_source']['asciiname'], alternate=res['hits']['hits'][0]['_source']['alternatenames'], \
            geonameid=res['hits']['hits'][0]['_source']['geonameid'])
    else:
        sr = SearchResult(name="NaT", score=0.0, asciiname="NaT", alternate="NaT", geonameid="00000") 
    return sr

def get_list_scores(es_con, idx, list_of_phrases):
    score_list = []
    for p in list_of_phrases:
        res = get_search_score(es_con, idx, p)
        score_list.append(res)
    # print score_list
    return score_list

reader = unicode_csv_reader(open('E:\\Dropbox\\[8]\\[cin]TA\\geonames\\ID.txt'), delimiter="\t", quoting=csv.QUOTE_MINIMAL)
current_nums = requests.get('http://localhost:9200/gaz-single-1/_count').json()['count']
print current_nums
i = 1
for row in reader:
    if i%1000 == 0:
        print i
    if i > current_nums:
        names = row[1] + ", " + row[2] + ", " + row[3]
        place = {"geonameid" : row[0], "names" : names}
        res = es.index(index='gaz-single-1', doc_type='toponym-single', id=row[0], body=place)
    i = i + 1
