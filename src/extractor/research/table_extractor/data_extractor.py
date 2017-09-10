## ATTEMP TO REWRITE THE PARSER
## NEW ALGORITHM

## 1. STRIP ALL BLANK LINES
## 2. SAVE ALL LINES IN MEMORY, TO BE PROCESSED
## 3. PARSE LINE PER LINE, SESUAI DENGAN KELAS LINE-NYA (H, D, A, G, N, T)

## Perlu bikin namedtuple untuk row dan table kah? Kayaknya perlu...
import os
import sys
import json
import pprint
import numpy as np
from bs4 import BeautifulSoup
from collections import namedtuple
from pandas import *
from transitions import Machine, core
from shutil import copyfile
from os.path import basename
from os.path import isfile
from os.path import exists
from os.path import abspath


class TableDetector(object):
    all_tables = []
    one_table = []
    def add_row_to_table(self, row):
        self.one_table.append(row)
    def add_table(self):
        self.all_tables.append(self.one_table)
        del self.one_table[:]

class DataExtractor(object):
    
    def __init__(self):

        self.Cell = namedtuple('Cell', ['text', 'rowspan'])
        self.Row = namedtuple('Row', ['list_of_cells', 'rowclass'])

        #### Begin of global variable ####
        self.STATES = ['start', 'in_title', 'in_header', 'in_group', 'in_data',
                  'in_aggregate', 'in_nonrel', 'fin', 'non_table']
        self.TRANSITIONS = [
            {'trigger': 'T', 'source': 'start', 'dest': 'in_title'},
            {'trigger': 'H', 'source': 'start', 'dest': 'in_header'},

            {'trigger': 'T', 'source': 'in_title', 'dest': 'in_title'},
            {'trigger': 'H', 'source': 'in_title', 'dest': 'in_header'},

            {'trigger': 'H', 'source': 'in_header', 'dest': 'in_header'},
            {'trigger': 'D', 'source': 'in_header', 'dest': 'in_data'},
            {'trigger': 'G', 'source': 'in_header', 'dest': 'in_group'},
            {'trigger': 'G', 'source': 'in_group', 'dest': 'in_group'},
            {'trigger': 'D', 'source': 'in_group', 'dest': 'in_data'},

            {'trigger': 'D', 'source': 'in_data', 'dest': 'in_data'},
            {'trigger': 'G', 'source': 'in_data', 'dest': 'in_group'},
            {'trigger': 'A', 'source': 'in_data', 'dest': 'in_aggregate'},
            {'trigger': 'A', 'source': 'in_aggregate', 'dest': 'in_aggregate'},
            {'trigger': 'N', 'source': 'in_data', 'dest': 'in_nonrel'},
            {'trigger': 'T', 'source': 'in_data', 'dest': 'fin'},
            {'trigger': 'H', 'source': 'in_data', 'dest': 'fin'},

            {'trigger': 'G', 'source': 'in_aggregate', 'dest': 'in_group'},
            {'trigger': 'N', 'source': 'in_aggregate', 'dest': 'in_nonrel'},
            {'trigger': 'D', 'source': 'in_aggregate', 'dest': 'in_data'},
            {'trigger': 'T', 'source': 'in_aggregate', 'dest': 'fin'},
            {'trigger': 'H', 'source': 'in_aggregate', 'dest': 'fin'},

            {'trigger': 'N', 'source': 'in_nonrel', 'dest': 'in_nonrel'},
            {'trigger': 'T', 'source': 'in_nonrel', 'dest': 'fin'},
            {'trigger': 'H', 'source': 'in_nonrel', 'dest': 'fin'},

            {'trigger': 'restart', 'source': '*', 'dest': 'start'},
            {'trigger': 'fin', 'source': '*', 'dest': 'fin'}
        ]
        self.TABLE_DETECTOR = TableDetector()
        self.MACHINE = Machine(self.TABLE_DETECTOR, states=self.STATES, transitions=self.TRANSITIONS, initial='start')
    #### End of Global variable ####

    def file_to_labels(self, label_file):
        with open(label_file) as labels:
            data = labels.readlines()
        for i in range(len(data)):
            # data[i] = data[i].split()
            data[i] = data[i].strip()
            if ',' in data[i]:
                data[i] = data[i].split(',')
            else:
                data[i] = data[i].split(' ')
        lab = [l[-1] for l in data]
        return lab

    def file_to_rowlist(self, table_file, label_list):
        soup = BeautifulSoup(open(table_file), 'html.parser')
        rows_element = soup.table.find_all("thead") + soup.table.find_all("tr") #assume 'thead' always occurs before 'tr' on a table
        rows_list = []
        for idx, r in enumerate(rows_element):
            if idx < len(label_list):
                if (label_list[idx] != 'B'):
                    cells_element = r.find_all('td') + r.find_all('th')
                    cells_in_row = []
                    for cell in cells_element:
                        if (cell.get('rowspan')):
                            rowspan_left = (int(cell['rowspan']) - 1)
                            c = self.Cell(text=cell.get_text().strip(), rowspan=rowspan_left)
                        else:
                            c = self.Cell(text=cell.get_text().strip(), rowspan=0)
                        cells_in_row.append(c)
                        if (cell.get('colspan')):
                            num_of_span = int(cell['colspan'])
                            for it in range(1, num_of_span):
                                if (cell.get('rowspan')):
                                    rowspan_left = (int(cell['rowspan']) - 1)
                                    c = self.Cell(text=cell.get_text().strip(), rowspan=rowspan_left)
                                else:
                                    c = self.Cell(text=cell.get_text().strip(), rowspan=0)
                                cells_in_row.append(c)
                    r_temp = self.Row(list_of_cells=cells_in_row, rowclass=label_list[idx])
                    rows_list.append(r_temp)
                else:
                    continue
        return rows_list

    def rowlist_to_tablelist(self, rows_list):
        list_of_tables = []
        a_table = []
        for it in range(len(rows_list)):
            # TODO: recheck transition! It's probable a transition from G-G or A-A happens
            try:
                if (rows_list[it].rowclass == 'H'):
                    self.TABLE_DETECTOR.H()
                    if (self.TABLE_DETECTOR.state == 'fin'):
                        self.list_of_tables.append(a_table)
                        self.TABLE_DETECTOR.restart()
                        # print "a_table %s" % a_table
                        a_table = []
                        self.TABLE_DETECTOR.H()
                elif (rows_list[it].rowclass == 'T'):
                    self.TABLE_DETECTOR.T()
                    if (self.TABLE_DETECTOR.state == 'fin'):
                        list_of_tables.append(a_table)
                        self.TABLE_DETECTOR.restart()
                        # print "a_table %s" % a_table
                        a_table = []
                        self.TABLE_DETECTOR.T()
                elif (rows_list[it].rowclass == 'G'):
                    self.TABLE_DETECTOR.G()
                elif (rows_list[it].rowclass == 'D'):
                    self.TABLE_DETECTOR.D()
                elif (rows_list[it].rowclass == 'A'):
                    self.TABLE_DETECTOR.A()
                else:  # rowclass == 'N'
                    self.TABLE_DETECTOR.N()
                a_table.append(rows_list[it])
                if (it == len(rows_list) - 1):
                    self.TABLE_DETECTOR.fin()
                    self.TABLE_DETECTOR.restart()
                    # print "a_table %s " % a_table
                    list_of_tables.append(a_table)
                    a_table = []
                    # print "to state %s " % table_detector.state
            except core.MachineError:
                # print "Not a table!"
                self.TABLE_DETECTOR.restart()
                continue
        return list_of_tables

    def get_table_title(self, a_table):
        title = [x for x in a_table if x.rowclass == 'T']
        table_title = ''
        for r in range(len(title)):  # penanganan untuk table yang T-row nya lebih dari 1, blm dicek
            table_title += title[r].list_of_cells[0].text
            table_title += ' '
        return table_title

    def get_table_notes(self, a_table):
        notes = [x for x in a_table if x.rowclass == 'N']
        table_notes = ''
        for r in range(len(notes)):  # penanganan untuk table yang N-row nya lebih dari 1, blm dicek
            row_note = ''
            if len(notes[r].list_of_cells) > 1:
                for i, c in enumerate(notes[r].list_of_cells):
                    if i > 0:
                        if c.text != notes[r].list_of_cells[i-1].text:
                            row_note += c.text
                            row_note += ' '
                        else:
                            continue
                    else:
                        row_note += c.text
                        row_note += ' '
            else:
                row_note = notes[r].list_of_cells[0].text

            table_notes += row_note
            table_notes += ' '
        return table_notes

    def list_to_matrix(self, a_list):
        for j in range(len(a_list) - 1):
            if (len(a_list[j].list_of_cells) > len(a_list[j + 1].list_of_cells)):
                for idx, cell in enumerate(a_list[j].list_of_cells):
                    if (cell.rowspan > 0):
                        if (idx < len(a_list[j + 1].list_of_cells)):
                            c = self.Cell(text=cell.text, rowspan=cell.rowspan - 1)
                            a_list[j + 1].list_of_cells.insert(idx, c)
                        else:
                            a_list[j + 1].list_of_cells.append(cell)

        final_matrix = []
        for k in range(len(a_list)):
            row = []
            for c in a_list[k].list_of_cells:
                # if (c.text != ''):
                row.append(c.text)
            final_matrix.append(row)
        return final_matrix

    def construct_key(self, header_matrix, header_list):
        keys = []
        if (len(header_list) > 1):  # penanganan untuk tabel dengan header row lebih dari 1
            num_of_cells = len(header_matrix[len(header_list) - 1])
            for it3 in range(num_of_cells):
                key = header_matrix[0][it3]
                for it2 in range(1, len(header_list)):
                    if (header_matrix[it2][it3] != header_matrix[it2 - 1][it3]):
                        key += ' ' + header_matrix[it2][it3]
                # if (key != ''):
                if key in keys:
                    counter = len([x for x in keys if x == key])
                    key = key + '-' + str(counter)
                keys.append(key)
        else:
            num_of_cells = len(header_matrix[len(header_list) - 1])
            for it in range(num_of_cells):
                key = header_matrix[0][it]
                # if (key != ''):
                if key in keys:
                    counter = len([x for x in keys if x == key])
                    key = key + '-' + str(counter)
                keys.append(key)
        for k in range(len(keys)):
            keys[k] = keys[k].replace(".","")
        return keys

    # def process_group_data(gda_row_list):

    def print_to_file(self, file_name, content_file):
        with open (file_name, 'w') as outfile:
            outfile.write(content_file)
            outfile.close()

    def extract_table(self, table_file, label_file):
        lab = self.file_to_labels(label_file)
        # print lab
        rows_list = self.file_to_rowlist(table_file, lab)
        # print rows_list
        list_tables = self.rowlist_to_tablelist(rows_list)
        # print len(list_tables)
        extracts = []
        for it in range(len(list_tables)):
            print "processing %s table from %s" % (it,table_file)
            t = list_tables[it]
            res = self.extract_data(t)
            extracts.append(res)
            # print json.dumps(res)
            # print_to_file("new_format.txt", json.dumps(res))
            # print_to_file("Extracts\\parsed-3\\kasuskhusus\\"+basename(table_file)+"_"+str(it)+".txt", json.dumps(res))
        return extracts

    def extract_data(self, a_table):
        out_json = {}
        data_arr = {}
        out_json['table_title'] = self.get_table_title(a_table)
        out_json['table_notes'] = self.get_table_notes(a_table)
        header = [x for x in a_table if x.rowclass == 'H']
        # print "=====HEADER====="
        # print header
        final_header_matrix = self.list_to_matrix(header)
        keys = self.construct_key(final_header_matrix, header)
        groups_idx = [x for x, i in enumerate(a_table) if i.rowclass == 'G']
        if (len(groups_idx) != 0):
            # process data per group
            data_group_arr = {}
            for it in range(len(groups_idx)):
                if it < len(groups_idx) - 1:
                    data_group = [x for i, x in enumerate(a_table) if
                                  (i > groups_idx[it] and i < groups_idx[it + 1] and x.rowclass == 'D')]
                    agregat_group = [x for i, x in enumerate(a_table) if
                                     (i > groups_idx[it] and i < groups_idx[it + 1] and x.rowclass == 'A')]
                else:
                    data_group = [x for i, x in enumerate(a_table) if (i > groups_idx[it] and x.rowclass == 'D')]
                    agregat_group = [x for i, x in enumerate(a_table) if (i > groups_idx[it] and x.rowclass == 'A')]

                final_data_group_matrix = self.list_to_matrix(data_group)
                # JSON construction
                temp_data_arr = {}
                count_temp_data_arr = 0
                for d in final_data_group_matrix:
                    data = {}
                    if (len(keys) == len(d)):  # else? ini bikin hasilnya jadi {} semua e.g. 1021-0
                        for itt in range(len(d)):
                            if (keys[itt] != '' and d[itt] != ''):
                                data[keys[itt]] = d[itt]
                    temp_data_arr["row-"+str(count_temp_data_arr)] = json.loads(json.dumps(data))
                    count_temp_data_arr += 1
                agg = {}
                if (len(agregat_group) > 0):
                    # process agregat row
                    agregat_data = {}
                    for z in xrange(len(agregat_group[0].list_of_cells) - 1, 0, -1):
                        agregat_data[keys[z]] = agregat_group[0].list_of_cells[z].text
                    # agg['_aggregate_'] = agregat_data
                    # temp_data_arr.append(json.loads(json.dumps(agg)))
                    temp_data_arr["_aggregate_"] = json.loads(json.dumps(agregat_data))
            #     data_group_arr[a_table[groups_idx[it]].list_of_cells[0].text] = temp_data_arr
                data_arr[a_table[groups_idx[it]].list_of_cells[0].text] = temp_data_arr
            # data_arr.append(data_group_arr)
        else:  # process all data in one
            agregat_group = [x for x in a_table if x.rowclass == 'A']

            data = [x for x in a_table if x.rowclass == 'D']

            final_data_matrix = self.list_to_matrix(data)
            count_data_arr = 0
            # JSON construction
            for d in final_data_matrix:
                data = {}
                if (len(keys) == len(d)):  # else?
                    for it in range(len(d)):
                        if (keys[it] != '' and d[it] != ''):
                            data[keys[it]] = d[it]
                # data_arr.append(json.loads(json.dumps(data)))
                data_arr["row-"+str(count_data_arr)] = json.loads(json.dumps(data))
                count_data_arr += 1
            agg = {}
            if (len(agregat_group) > 0):
                # process agregat row
                agregat_data = {}
                # print len(keys)
                for z in xrange((len(agregat_group[0].list_of_cells) - 1), 0, -1):
                    # print z
                    agregat_data[keys[z]] = agregat_group[0].list_of_cells[z].text
                # agg['_aggregate_'] = agregat_data
                # data_arr.append(json.loads(json.dumps(agg)))
                data_arr["_aggregate_"] = agregat_data
        out_json['table_data'] = data_arr
        self.print_to_file('test.txt', json.dumps(out_json))
        return out_json

    def get_grouped(self, l):
        grouplist = []
        group = []
        for i in xrange(len(l)):
            print i
            if len(group) == 0:
                group.append(l[i])
            elif l[i]-group[-1] == 1:
                group.append(l[i])
            else:
                grouplist.append(group)
                group = []
                group.append(l[i])
            if i == (len(l) - 1):
                grouplist.append(group)
        # print grouplist
        return grouplist

    def extract_data_g(self, a_table):
        out_json = {}
        data_arr = {}
        out_json['table_title'] = self.get_table_title(a_table)
        out_json['table_notes'] = self.get_table_notes(a_table)
        header = [x for x in a_table if x.rowclass == 'H']
        # print "=====HEADER====="
        # print header
        final_header_matrix = self.list_to_matrix(header)
        keys = self.construct_key(final_header_matrix, header)
        groups_idx = [x for x, i in enumerate(a_table) if i.rowclass == 'G']
        if (len(groups_idx) != 0):
            grouped = self.get_grouped(groups_idx)
            # process data per group
            data_group_arr = {}
            for it in range(len(grouped)):
                if it < len(groups_idx) - 1:
                    data_group = [x for i, x in enumerate(a_table) if
                                  (i > grouped[it][-1] and i < grouped[it + 1][0] and x.rowclass == 'D')]
                    agregat_group = [x for i, x in enumerate(a_table) if
                                     (i > grouped[it][-1] and i < grouped[it + 1][0] and x.rowclass == 'A')]
                else:
                    data_group = [x for i, x in enumerate(a_table) if (i > grouped[it][-1] and x.rowclass == 'D')]
                    agregat_group = [x for i, x in enumerate(a_table) if (i > grouped[it][-1] and x.rowclass == 'A')]

                final_data_group_matrix = self.list_to_matrix(data_group)
                # JSON construction
                temp_data_arr = {}
                count_temp_data_arr = 0
                for d in final_data_group_matrix:
                    data = {}
                    if (len(keys) == len(d)):  # else? ini bikin hasilnya jadi {} semua e.g. 1021-0
                        for itt in range(len(d)):
                            if (keys[itt] != '' and d[itt] != ''):
                                data[keys[itt]] = d[itt]
                    temp_data_arr["row-"+str(count_temp_data_arr)] = json.loads(json.dumps(data))
                    count_temp_data_arr += 1
                agg = {}
                if (len(agregat_group) > 0):
                    # process agregat row
                    agregat_data = {}
                    for z in xrange(len(agregat_group[0].list_of_cells) - 1, 0, -1):
                        agregat_data[keys[z]] = agregat_group[0].list_of_cells[z].text
                    temp_data_arr["_aggregate_"] = json.loads(json.dumps(agregat_data))
                key_group = self.get_key_group(a_table, grouped[it])
                # data_arr[a_table[groups_idx[it]].list_of_cells[0].text] = temp_data_arr
        else:  # process all data in one
            agregat_group = [x for x in a_table if x.rowclass == 'A']

            data = [x for x in a_table if x.rowclass == 'D']

            final_data_matrix = self.list_to_matrix(data)
            count_data_arr = 0
            # JSON construction
            for d in final_data_matrix:
                data = {}
                if (len(keys) == len(d)):  # else?
                    for it in range(len(d)):
                        if (keys[it] != '' and d[it] != ''):
                            data[keys[it]] = d[it]
                # data_arr.append(json.loads(json.dumps(data)))
                data_arr["row-"+str(count_data_arr)] = json.loads(json.dumps(data))
                count_data_arr += 1
            agg = {}
            if (len(agregat_group) > 0):
                agregat_data = {}
                for z in xrange((len(agregat_group[0].list_of_cells) - 1), 0, -1):
                    agregat_data[keys[z]] = agregat_group[0].list_of_cells[z].text
                data_arr["_aggregate_"] = agregat_data
        out_json['table_data'] = data_arr
        return out_json

    def get_key_group(self, a_table, indices):
        keys = [x for i, x in enumerate(a_table) if i in indices]
        key_group_matrix = self.list_to_matrix(keys)
        retval = []
        for j in xrange(len(key_group_matrix[0])):
            key = ""
            for k in xrange(len(indices)):
                key = key + key_group_matrix[k][j]
                retval.append(key)
        # print retval
        return retval

# de = DataExtractor()
# extracts = de.extract_table('clean_html/test/0-test.html','row_feature_extraction/13/0-test-features.txt')
# js = json.dumps(extracts)
# print(js)