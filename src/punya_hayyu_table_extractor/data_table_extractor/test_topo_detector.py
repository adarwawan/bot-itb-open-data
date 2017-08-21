from toponym_indexing import ToponymDetector
import json
import os
from os.path import isfile

src_dir = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Extracts\\parsed-3\\"
dest_dir = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Extracts\\parsed-3\\with-topo-cols\\"

testfileno = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Extracts\\parsed-3\\24clear.xml-table-0.html_0.txt"
testfileyes = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Extracts\\parsed-3\\72clear.xml-table-0.html_0.txt"
topoatheader = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Extracts\\parsed-3\\kasuskhusus\\topoatheader.html_0.txt"
topomorethanone = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Extracts\\parsed-3\\kasuskhusus\\topomorethanone.html_0.txt"

for f in os.listdir(src_dir):
	current = os.path.join(src_dir, f)
	if isfile(current):
		print f
		with open(current, 'r') as infile:
			data = infile.read()
		td = ToponymDetector()
		js = json.loads(data)
		lok = []
		td.get_leave_keys(js['table_data'], lok)
		topo_key = td.get_toponym_keys(lok, js['table_data'])
		print lok
		print topo_key
		if len(topo_key) > 0:
			td.add_toponym_index(js['table_data'], topo_key)
			outfile = os.path.join(dest_dir, f)
			with open(outfile, 'w') as of:
				of.write(json.dumps(js))
		else:
			continue
