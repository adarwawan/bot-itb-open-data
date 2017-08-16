# DRIVER FOR CRF Learner

from Learner import CRFLearner
import sys
from sklearn.cross_validation import train_test_split
import os


ftrain_noyear_all = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Features\\20160903_laporan\\all_features_noyear.txt"
ftrain_noyear_valid = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Features\\20160903_laporan\\wononvalid-features.txt"
ftrain_all = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Features\\20160903_laporan_withyear\\all_features_year.txt"
ftrain_valid = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Features\\20160903_laporan_withyear\\wononvalid_year.txt"
model_dir = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\crf_learner\\models\\"
iterations = [250, 350]
possible_trans = [True, False]
noyears = [ftrain_noyear_valid, ftrain_noyear_all]

# for i in iterations:
# 	for j in possible_trans:
# 		for k in xrange(len(noyears)):
# 			learner = CRFLearner(i, j)
# 			train_corpus = learner.prepareCorpus(noyears[k])
# 			# print train_corpus
# 			X_train = [learner.table2features(s) for s in train_corpus]
# 			# print X_train
# 			Y_train = [learner.table2labels(s) for s in train_corpus]
# 			# print Y_train
# 			if __name__ == '__main__':
# 				# crosval_result = learner.crossValidation(3, X_train, Y_train)
# 				# print crosval_result
# 				sys.stdout = open('CRFExperiment.log', 'a')

# 				grid_scores, best_param, best_score = learner.crossValidation(3, X_train, Y_train)
# 				print best_param
# 				X_train, X_test, Y_train, Y_test = train_test_split(X_train, Y_train, test_size=0.2, random_state=42)
# 				if k == 0:
# 					ds = "valid"
# 				else:
# 					ds = "all"
# 				modelname = "noyear_" + ds + "_" + str(i) + "_" + str(j) + ".model"
# 				train = learner.buildModel2(X_train, Y_train, X_test, Y_test, os.path.join(model_dir, modelname), best_param['c1'], best_param['c2'])
# 				print modelname
# 				print train

modelfiles = [
	'noyear_all_350_False.model',
	'noyear_valid_350_False.model',
	'noyear_all_350_True.model',
	'noyear_valid_350_True.model',
	'noyear_all_250_False.model',
	'noyear_valid_250_False.model',
	'noyear_all_250_True.model',
	'noyear_valid_250_True.model',
	'noyear_valid_200_false.model',
	'noyear_valid_200_true.model',
	'noyear_valid_400_false.model',
	'noyear_valid_400_true.model',
	'noyear_all_400_false.model',
	'noyear_all_400_true.model',
	'noyear_all_200_false.model',
	'noyear_all_200_true.model'
]
test_file = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Features\\20160903_laporan\\test_nonvalid.txt"
# for f in modelfiles:
# 	if __name__ == '__main__':
# 		learner = CRFLearner(100, True)
# 		test_corpus = learner.prepareCorpus(test_file)
# 		test_result = learner.testPredict(test_corpus, os.path.join(model_dir, f))
# 		sys.stdout = open('CRFExperiment-unvalid.log', 'a')
# 		print("%s \n" % f)
# 		print test_result
learner = CRFLearner(100, True)
test_corpus = learner.prepareCorpus(test_file)
test_result = learner.testPredict(test_corpus, os.path.join(model_dir, modelfiles[0]))
# sys.stdout = open('CRFExperiment-unvalid.log', 'a')
print("%s \n" % modelfiles[0])
print test_result