from rule_based_extractor import RuleBasedExtractor
from feature_extractor import RowFeatureExtractor
from Learner import CRFLearner
from data_extractor import DataExtractor
import json
import os, shutil
from os.path import basename
import sys

class AutoExtract(object):
    """docstring for AutoExtract"""
    def __init__(self):
        super(AutoExtract, self).__init__()
      
    def clearFile(self, dir3):
        for the_file in os.listdir(dir3):
            file_path = os.path.join(dir3, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    def print_to_file(self, file_name, content_file):
        with open (file_name, 'w') as outfile:
            outfile.write(content_file)
            outfile.close()

def main(argv):
    if len(argv) != 1:
        print 'usage: python rule_based_extractor.py <url>'
        sys.exit(2)    
    
    

    AE = AutoExtract()
    AE.clearFile("new_feature_extraction/test")
    AE.clearFile("row_feature_extraction/test")
    AE.clearFile("clean_html/test")
    AE.clearFile("result")
    output_dir = "clean_html/"
    filename = "test.html"
    sub_folder = os.path.splitext(basename(filename))[0] + "/"
    print sub_folder
    rbe = RuleBasedExtractor(output_dir+sub_folder, argv[0])
    body_soup = rbe.getBody()
    tables = rbe.getCandidatesTable(body_soup)
    tables = rbe.getCandidatesUnorderedList(body_soup)
    tables = rbe.getCandidatesOrderedList(body_soup)

    input_dir = "clean_html/test/"
    output_dir = "row_feature_extraction/test/"
    new_output_dir = "new_feature_extraction/test/"
    filenames = os.listdir(input_dir)
    filenames.sort()
    print(filenames)
    crf = CRFLearner(250,False)
    train_file = "160_bpsitb.txt"
    old_file_corpus = "-test-features.txt"
    model_file = "table.model"
    i = 0
    for filename in filenames:
        sub_folder = os.path.splitext(basename(filename))[0] + "/"
        rfe = RowFeatureExtractor(input_dir + filename, output_dir)
        table_soup = rfe.getTable()
        rfe.processTable(table_soup)
        pp = rfe.getFeatures()
        crf = CRFLearner(250,False)
        file_corpus = output_dir + str(i) + old_file_corpus
        test_corpus = crf.prepareATest(file_corpus)
        y = crf.predictAtable([test_corpus], model_file)
        for j in xrange(0,len(pp)):
            fname, ext = basename(input_dir + filename).split('.')
            fout = os.path.join(new_output_dir, fname + "-features.txt")
            dataset = pp[j].replace('\n', '')
            with open(fout, 'a+') as f:
                f.write(dataset + ',' + y[0][j] + '\n')
        de = DataExtractor()
        file_html = input_dir + str(i) + '-test.html'
        feature = new_output_dir + str(i) + '-test-features.txt'
        extracts = de.extract_table(file_html,feature)
        js = json.dumps(extracts)
        AE.print_to_file("result/" + str(i) + '-test.txt', js)
        i += 1

if __name__ == "__main__":
   main(sys.argv[1:])