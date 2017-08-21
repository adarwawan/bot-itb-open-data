import os
import json
import jsontree
import pymongo
from pymongo import MongoClient
from collections import namedtuple

PREP_DICT = ['Provinsi', 'Kota']

client = MongoClient('localhost', 27017)
db = client['table_extractor']
places = db['places']

file_ext = "E:\\Dropbox\\[8]\\[cin]TA\\RawData\\extract_tables8\\EXT_108clear.xml-table-0.html.txt"
with open(file_ext, 'r') as infile:
    data = infile.read()
print data
json_obj = jsontree.loads(data)
json_table_data = jsontree.loads(jsontree.dumps(json_obj['table_data']))
print "items %s " % json_table_data
# if json_table_data.has_keys():
#     print(json_table_data.keys())

# Baru untuk nested 2 level, TODO: tangani nested yang lebih dari 2 level
for key, value in json_obj.iteritems():
    val_temp = value[0] #kalau nggak 0 bakal error
    try:
        keys = val_temp.keys()
        json_child = []
        for k in keys:
            val_temp2 = val_temp[k]
            print "val_temp2 %s" % val_temp2
            json_child.append(val_temp2)
    except AttributeError:
        print "Error!"
    else:
        for i in range(len(json_child)):
            current = json_child[i][0] #ambil salah satu element aja (element pertama), asumsi key-nya bakal sama terus
            # try:
            c_keys = current.keys()
            list_key_prep = []
            list_of_toponym = []
            for ck in c_keys:
                if ck in [y for y in PREP_DICT]:
                    for i2 in range(len(json_child[i])):
                        list_of_toponym.append(json_child[i][i2][ck])
                    # print list_val_ck
                    score = 0
                    for tel in list_of_toponym:
                        if (places.find_one({'$text': {'$search': tel}})):
                            score += 1
                    # print score
                    # print len(list_of_toponym)
                    if (score > 0.9 * len(list_of_toponym)): # TODO: decide threshold value
                        list_key_prep.append(ck)
                # cek bahwa semua value dengan key ck merupakan toponym (bandingkan dengan geonames)
                # jika lolos, baru construct list of object untuk tiap toponym
            if (len(list_key_prep) > 0): # gimana kalau len(list_key_prep) nya lebih dari 1?
                attrs = [str(ok) for ok in c_keys if ok != list_key_prep[0]]
                # print attrs
                list_of_obj = []
                for j in range(len(json_child[i])):
                    a_obj = {}
                    all_attrs = {}
                    for a in attrs:
                        all_attrs[a] = json_child[i][j][a]
                    a_obj[json_child[i][j][list_key_prep[0]]] = all_attrs
                    print a_obj
                    list_of_obj.append(a_obj)
            # for oj in list_of_obj:
            #     current_val = oj.values()
            #     print current_val
