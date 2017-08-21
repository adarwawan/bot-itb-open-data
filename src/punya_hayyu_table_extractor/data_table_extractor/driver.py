# DRIVER FOR data_table_extractor

from feature_extractor import RowFeatureExtractor
from rule_based_extractor import RuleBasedExtractor
from data_extractor_2 import DataExtractor
import sys
import os
from os.path import basename
from os.path import isfile
from os.path import exists
from os.path import abspath


def labelFile(labeledfile, nonlabeledfile):
	with open(labeledfile, 'r') as lf:
		label_data = lf.readlines()
	labels = [l[-2] for l in label_data]
	# print labels
	with open(nonlabeledfile, 'r') as nl:
		nl_data = nl.readlines()
		nl.close()
	new_lines = []
	for i, d in enumerate(nl_data):
		currentline = d.strip() + "," + labels[i] + "\n"
		new_lines.append(currentline)
	print new_lines
	with open(nonlabeledfile, 'w') as newlfile:
		newlfile.writelines(new_lines)

HTML_dir = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\HTML\\"
out_feature_dir = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Features\\20160903_laporan\\"
feature_with_label = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Features\\"
year_out_feature_dir = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Features\\20160903_laporan_withyear\\"

## FEATURE EXTRACTION ##
# for file in os.listdir(HTML_dir):
# 	current = os.path.join(HTML_dir, file)
# 	checkfirst = os.path.join(year_out_feature_dir, file+"-features.txt")
# 	if (isfile(current) and not os.path.exists(checkfirst)):
# 		current_file_name = basename(current)
# 		rfe = RowFeatureExtractor(current, os.path.join(year_out_feature_dir, current_file_name+"-features.txt"))
# 		table_soup = rfe.getTable()
# 		rfe.processTable(table_soup)

## FEATURE FILE LABELING ##
# for file in os.listdir(feature_with_label):
# 	current = os.path.join(feature_with_label, file)
# 	if isfile(current):
# 		for file2 in os.listdir(year_out_feature_dir):
# 			if file == file2:
# 				current2 = os.path.join(year_out_feature_dir, file2)
# 				labelFile(current, current2)

## FEATURE FILE CONCATENATION ##
# all_lines = []
# for file in os.listdir(year_out_feature_dir):
# 	current = os.path.join(year_out_feature_dir, file)
# 	with open(current, 'r') as infile:
# 		d = infile.readlines()
# 	all_lines = all_lines + d
# 	all_lines.append("\n")
# with open(os.path.join(year_out_feature_dir, "all_features_year.txt"), 'w') as outfile:
# 	outfile.writelines(all_lines)

## RULE BASED EXTRACTOR ##
# rawdata_dir ="E:\\Dropbox\\[8]\\[cin]TA\\RawData\\downloaded\\ClearHtml\\"
# result_dir = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\DemoData\\HTMLTable\\"
# for file in os.listdir(rawdata_dir):
# 	current = os.path.join(rawdata_dir, file)
# 	if isfile(current):
# 		rbe = RuleBasedExtractor(current, result_dir)
# 		body_soup = rbe.getBody()
# 		tables = rbe.getCandidatesTable(body_soup)

## DATA EXTRACTOR ##
de = DataExtractor()
htmlfile = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\HTML\\eval2\\kasuskhusus\\topomorethanone.html"
featurefile = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Features\\kasuskhusus\\topomorethanone.txt"
extracts = de.extract_table(htmlfile, featurefile, ',')
print extracts
