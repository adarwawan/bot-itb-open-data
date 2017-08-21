import types
import json
import os
import sys
# from es_geonames import *
# from data_extractor_2 import print_to_file
from elasticsearch import Elasticsearch
from os.path import basename
from os.path import isfile
import pandas as pd
from scipy import stats

class ToponymDetector(object):
    def __init__(self):
        self.preposition_dict = ['provinsi', 'kota', 'daerah', 'regional', 'kabupaten', 'kecamatan']
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    def get_leave_keys(self, iterable, list_of_keys):
        """
        :param iterable: json_obj['table_data']
        :param list_of_keys: list of leave keys
        :return:
        """
        if isinstance(iterable, list):
            for ins in iterable:
                # print ins
                if isinstance(ins, dict):
                    self.get_leave_keys(ins, list_of_keys)

        else: #isinstance(iterable, dict):
            if self.is_leave_dict(iterable):
                keys = [k for k, v in iterable.iteritems()]
                for k in keys:
                    if k not in list_of_keys:
                        list_of_keys.append(k)
            else: # isinstance(iterable, dict):
                for k, v in iterable.iteritems():
                    self.get_leave_keys(v, list_of_keys)
            # else:
            #     get_keys(iterable, list_of_keys)

    def get_dict_element(self, str_key):
        """ str_key = key that contains toponym preposition """
        for e in self.preposition_dict:
            if e in str_key.lower():
                return e
            else:
                pass

    def is_leave_dict(self, iterable):
        """
        :param iterable: dictionary OR list
        :return: true if dictionary doesn't contain list of dicts or another dicts
        """
        retval = True
        if isinstance(iterable, list):
            retval = False
        else:
            for k, v in iterable.iteritems():
                if isinstance(v, list) or isinstance(v, dict):
                    retval = False
                    break
        return retval

    def get_leave_dicts(self, iterable):
        """
        :param iterable: dictionary, json_obj['table_data']
        :return: list of leave dicts
        """
        list_of_dicts = []
        if isinstance(iterable, dict):
            if self.is_leave_dict(iterable):
                list_of_dicts.append(iterable)
            else:
                for k, v in iterable.iteritems():
                    list_of_dicts = list_of_dicts + self.get_leave_dicts(v)
        else: # isinstance(iterable, list):
            for ins in iterable:
                list_of_dicts = list_of_dicts + self.get_leave_dicts(ins)
        return list_of_dicts

    def get_allval_infield(self, iterable, str_key):
        leave_dicts = self.get_leave_dicts(iterable)
        retval = []
        for ld in leave_dicts:
            if str_key in ld:
                # print ld[str_key]
                retval.append(ld[str_key])
        return retval

    # def add_toponym_index(iterable):
    #     """
    #     :param iterable: dictionary, json_obj['table_data']
    #     :return: void, modified iterable
    #     """
    #     if isinstance(iterable, dict):
    #         if is_leave_dict(iterable):
    #             list_of_dicts.append(iterable)
    #         else:
    #             for k, v in iterable.iteritems():
    #                 list_of_dicts = list_of_dicts + get_leave_dicts(v)
    #     else: # isinstance(iterable, list):
    #         for ins in iterable:
    #             list_of_dicts = list_of_dicts + get_leave_dicts(ins)

    def key_checker(self, str_key):
        list_words = str_key.split(" ")
        is_toponym_key = False
        if len(list_words) > 1:
            for w in list_words:
                if w in self.preposition_dict:
                    is_toponym_key = True
                    break
        else:
            if list_words[0] in self.preposition_dict:
                is_toponym_key = True

        return is_toponym_key

    def get_toponym_keys(self, list_of_keys, iterable):
        """
        :param list_of_keys: list of leave keys
        :return: list of key for candidate toponym
        """
        # TODO: apply toponym_rule_checker first
        retval = []
        for k in list_of_keys:
            if self.key_checker(k.lower()):
                canditate_toponym = self.get_allval_infield(iterable, k)
                if self.cols_rule_checker(canditate_toponym):
                    gaz_checker = self.gazetteer_checker(canditate_toponym, self.get_dict_element(k))
                    if gaz_checker > (0.9 * len(canditate_toponym)):
                        retval.append(k)
        # if len(retval) == 0:
        #     for k in list_of_keys:
        #         if self.toponym_rule_checker(k):
        #             gaz_score = self.check_gaz(k, None)
        #             if gaz_score > 1:
        #                 retval.append(k)
        return retval

    def check_gaz(self, str_topo, str_key=None):
        if str_key == None:
            query = str_topo
        else:
            query = "%s %s" % (str_key, str_topo)
        query_body4 = {
            "size" : 1,
            "query" : {
                "bool" : {
                    "must" : {
                        "multi_match": { 
                          "fields":  [ "name", "asciiname", "alternatenames" ], 
                          "query":     query, 
                          "fuzziness": "AUTO" 
                        } 
                    },
                    "should" : {
                        "multi_match": { 
                          "fields":  [ "name", "asciiname", "alternatenames" ], 
                          "query":     str_topo, 
                          "fuzziness": 0 
                        }
                    }
                }
            }
        }
        res = self.es.search(index="gir", body=query_body4)
        if len(res['hits']['hits']) > 0:
            print (res['hits']['hits'][0]['_source']['name'], res['hits']['max_score'])
            return res['hits']['max_score']
        else:
            return 0

    # def alternate_toponym_keys(self, list_of_keys):
    #     """
    #     Used when toponym_keys = []
    #     Arguments:
    #         list_of_keys {[list]} -- all keys of the table
    #     """
    #     alt_toponym_keys = []
    #     for k in list_of_keys:
    #         if self.toponym_rule_checker(k):
    #             sr = self.get_search_score(es, 'gir', k)
    #             if sr.score > 1:
    #                 alt_toponym_keys.append(k)
    #     return alt_toponym_keys

    def get_candidates_toponym(self, list_of_dicts, key_name):
        """
        :param list_of_dicts: list of leave dicts
        :param key_name: key for candidate toponym
        :return: list of candidate toponyms
        """
        # TODO: apply toponym_rule_checker first
        retval = []
        for d in list_of_dicts:
            if key_name in d:
                retval.append(d[key_name])
        return retval

    def get_toponym_data(self, list_of_dicts, key_toponym):
        """
        :param list_of_dicts: list of leave dicts
        :param key_toponym: key for candidates toponym
        :return: list of dicts with toponym as the outest key
        """

        retval = []
        for d in list_of_dicts:
            tmp = {}
            if key_toponym in d:
                tmp2 = {}
                for k, v in d.iteritems():
                    if k != key_toponym:
                        tmp2[k] = v
                tmp[d[key_toponym]] = tmp2
                retval.append(tmp)
            else:
                pass
        return retval


    def add_toponym_index(self, table_data, key_name):
        """   
        add toponym index for 'table_data'
        Arguments:
            table_data {[list, dict]} -- json['table_data']
            key_name {[list]} -- list of toponym keys
        """
        # print table_data
        # print key_name
        if not self.is_leave_dict(table_data):
            if isinstance(table_data, list):
                for i in xrange(len(table_data)):
                    if not self.is_leave_dict(table_data[i]):
                        self.add_toponym_index(table_data[i], key_name)
                    else:
                        table_data[i] = self.construct_topo_index(table_data[i], key_name)
                        # print table_data[i]
            else: #table_data is dictionary
                for k, v in table_data.iteritems():
                    if not self.is_leave_dict(v):
                        self.add_toponym_index(v, key_name)
                    else:
                        table_data[k] = self.construct_topo_index(table_data[k], key_name)
                        # print table_data[k]
        else:
            table_data = self.construct_topo_index(table_data, key_name)
            # print table_data
        return table_data

    def construct_topo_index(self, dicts, list_key):
        """ dicts: datarow, list_key: keys of fields that contains toponym """
        dicts = dict((k.lower(), v) for k, v in dicts.iteritems())
        topo_index = ""
        # print list_key
        for a_key in list_key:
            if a_key.lower() in dicts:
                topo_index += dicts[a_key.lower()] + "\t"
        dicts['toponym'] = topo_index
        return dicts

    def toponym_rule_checker(self, phrase):
        non_number = True
        is_short = True
        in_max_phrases = True
        if any(char.isdigit() for char in phrase):
            non_number = False
        if len(phrase) > 200:
            is_short = False
        # if len(phrase.split(" ")) > 7:
        #     in_max_phrases = False
        return (non_number and is_short and in_max_phrases)

    def cols_rule_checker(self, values):
        counter = 0
        for v in values:
            if self.toponym_rule_checker(v):
                counter = counter + 1
        if (counter >= (0.9 * len(values))):
            return True
        else:
            return False

    def gazetteer_checker(self, values, str_key):
        counter = 0
        for p in values:
            gaz_score = self.check_gaz(p, str_key)
            if gaz_score > 1:
                counter = counter + 1
        return counter


    # input: dict, output: list of dict that have a key key_name TODO: pikirin apa bener butuh method ini?
    # def get_key_path(self, iterable, key_name):
    #     list_of_dict = []
    #     if isinstance(iterable, dict):
    #         keys = [k for k, v in iterable.iteritems()]

    #     else:
    #         pass
    #     return list_of_dict

# ext_dir = "Extracts\\parsed-3\\"
# topo_indexed_dir = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_tabel_extractor\\Topo_indexed\\2\\"

# for f in os.listdir(ext_dir):
#     current = os.path.join(ext_dir, f)
#     print current
#     if isfile(current):
#         with open(current, 'r') as infile:
#             data = infile.read()
#             infile.close()
#         # print type(data)
#         json_obj = json.loads(data)
#         # print type(json_obj['table_data'])
#         lok = []
#         get_leave_keys(json_obj['table_data'], lok)
#         list_of_toponym_key = get_toponym_keys(lok)

#         if len(list_of_toponym_key) > 0:
#             # try:
#             json_obj['table_data'] = add_toponym_index(json_obj['table_data'],list_of_toponym_key)
#             with open ("Topo_indexed\\2\\"+basename(current), 'w+') as outfile:
#                 outfile.write(json.dumps(json_obj))
#                 outfile.close()
            # break
            # print_to_file(topo_indexed_dir+basename(current), json.dumps(json_obj))
            # except:
            #     print basename(current)
            #     print sys.exc_info()
            #     break    

# with open('E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Extracts\\parsed-2\\108clear.xml-table-0.html_0.txt', 'r') as infile:
#     data = infile.read()
# # print type(data)
# json_obj = json.loads(data)
# add_toponym_index(json_obj['table_data'], ['provinsi'])
# print json_obj['table_data']

# leave_dicts = get_leave_dicts(json_obj['table_data'])
# print len(leave_dicts)
# candidates = get_candidates_toponym(leave_dicts, list_of_toponym_key[0]) # nyoba satu kolom toponym dulu
# print candidates
# scores = get_list_scores(es, 'gir', candidates)
# sr_names = [x.name for x in scores]
# sr_scores = [y.score for y in scores]
# sr_geoid = [z.geonameid for z in scores]

# print sr_geoid

# different = []
# for k in xrange(len(sr_geoid)):
#     if sr_geoid[k] == sr_geoid2[k]:
#         print(1)
#     else:
#         different.append(k)
#         print(0)
# print different

# df_score = pd.DataFrame({
#         'score_1' : sr_scores,
#         'score_2' : sr_scores2
#     })
# print(df_score.describe())
# z_stat, p_val = stats.ranksums(sr_scores, sr_scores2)
# print "p_val : %s" % p_val
# print(stats.normaltest(sr_scores))
# print(stats.normaltest(sr_scores2)) 

# pd.set_option('display.max_rows', 200)
# df = pd.DataFrame({
#     'from_table': candidates,
#     'sr_names': sr_names,
#     'sr_asciiname' : [x.asciiname for x in scores],
#     'sr_alternate' : [x.alternate for x in scores],
#     'sr_scores': sr_scores
# })
# print df
# df.to_csv('Notes\\gir-q3.csv', index=False, encoding='utf-8')
# pd.reset_option('display.max_rows')

# print get_toponym_data(lod, get_toponym_keys(lok)[0])
