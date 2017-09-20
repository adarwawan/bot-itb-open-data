from rule_based_extractor import RuleBasedExtractor
from feature_extractor import RowFeatureExtractor
from Learner import CRFLearner
from data_extractor import DataExtractor
import json
import os, shutil
from os.path import basename
import sys
import codecs

class TableExtractor(object):
    """docstring for TableExtractor"""
    def __init__(self, dirout, url):
        super(TableExtractor, self).__init__()
        self.url = url
        self.dirout = dirout
        self.clearAll()
        self.input_dir = dirout + "clean_html/test/"
        self.output_dir = dirout + "row_feature_extraction/test/"
        self.new_output_dir = dirout + "new_feature_extraction/test/"
        self.train_file = dirout + "160_bpsitb.txt"
        self.model_file = dirout + "table.model"
        self.rule_based_extractor()
        self.learning()

    def clearFile(self, dir3):
        for the_file in os.listdir(dir3):
            file_path = os.path.join(dir3, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    def clearAll(self):
        self.clearFile(self.dirout + "new_feature_extraction/test")
        self.clearFile(self.dirout + "row_feature_extraction/test")
        self.clearFile(self.dirout + "clean_html/test")
        self.clearFile(self.dirout + "result")

    def print_to_file(self, file_name, content_file):
        with codecs.open (file_name, 'w', encoding="UTF-8") as outfile:
            outfile.write(content_file)
            outfile.close()

    def rule_based_extractor(self):
        rbe = RuleBasedExtractor(self.dirout, self.url)
        body_soup = rbe.getBody()
        tables = rbe.getCandidatesTable(body_soup)    

    def learning(self):
        filenames = os.listdir(self.input_dir)
        filenames.sort()
        # print(filenames)
        crf = CRFLearner(250,False)
        old_file_corpus = "-test-features.txt"
        i = 0
        for filename in filenames:
            sub_folder = os.path.splitext(basename(filename))[0] + "/"
            filename = str(i) + "-test.html"
            rfe = RowFeatureExtractor(self.input_dir + filename, self.output_dir)
            table_soup = rfe.getTable()
            rfe.processTable(table_soup)
            pp = rfe.getFeatures()
            file_corpus = self.output_dir + str(i) + old_file_corpus
            test_corpus = crf.prepareATest(file_corpus)
            y = crf.predictAtable([test_corpus], self.model_file)
            for j in xrange(0,len(pp)):
                fname, ext = basename(self.input_dir + filename).split('.')
                fout = os.path.join(self.new_output_dir, fname + "-features.txt")
                dataset = pp[j].replace('\n', '')
                with open(fout, 'a+') as f:
                    f.write(dataset + ',' + y[0][j] + '\n')
            de = DataExtractor()
            file_html = self.input_dir + str(i) + '-test.html'
            feature = self.new_output_dir + str(i) + '-test-features.txt'
            extracts = de.extract_table(file_html,feature)
            if len(extracts) != 0:
                table_data = extracts[0]['table_data']
                texts = ""
                # print table_data
                for key, value in table_data.items():
                    text = ''
                    for key2, value2 in value.items():
                            text = ' '.join(value2.split()) + ". " + text
                    if (text.strip() != ""):
                        texts = texts + text + "\n"
                js = json.dumps(extracts)
                self.print_to_file(self.dirout + "result/" + str(i) + '-table.txt', texts)
            i += 1 

def main(argv):
    if len(argv) != 1:
        print 'usage: python rule_based_extractor.py <url>'
        sys.exit(2)    

    output_dir = ""
    url = argv[0]

    AE = TableExtractor(output_dir, url)

        

if __name__ == "__main__":
   main(sys.argv[1:])
