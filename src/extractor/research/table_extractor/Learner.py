from itertools import chain
import nltk
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn
import pycrfsuite
import string
from sklearn.metrics import make_scorer
# from sklearn.cross_validation import cross_val_score
# from sklearn.grid_search import RandomizedSearchCV
import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
import scipy
from collections import Counter
import sys
import pickle

class CRFLearner(object):
    def __init__(self, max_iterations, all_possible_transitions):
        self.crf = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            max_iterations=max_iterations,
            all_possible_transitions=all_possible_transitions
        )
    
    def prepareATest(self, file_test):
        with open(file_test, "rb") as table:
            data = table.readlines()
        ready_corpus = []
        for j in range(len(data)):
            temp = string.rstrip(data[j],'\r?\n')
            to_list = temp.split(",")
            ready_corpus.append(to_list)
        return ready_corpus
    
    def prepareCorpus(self, file_train):
        with open(file_train, "rb") as table:
            data = table.readlines()
#         print data
        corpus = []
        element = []
        for i in range(len(data)):
            if len(data[i]) > 2:
                element.append(data[i])
            else:
                corpus.append(element)
                element = []
#         print len(corpus)
        ready_corpus = []
        for j in range(len(corpus)):
            tmp_corpus = []
            for k in range(len(corpus[j])):
                temp = string.rstrip(corpus[j][k],'\r?\n')
                to_list = temp.split(",")
#                 print to_list
                tmp_corpus.append(to_list)
            ready_corpus.append(tmp_corpus)
#         print ready_corpus
        return ready_corpus
    
    def row2features(self, table, i):
        features = [
            'ismerged=' + str(table[i][0]),
            'ishead=' + str(table[i][1]),
            'isempty=' + str(table[i][2]),
            'isshorttext=' + str(table[i][3]),
            'islongtext=' + str(table[i][4]),
            'isnumeric=' + str(table[i][5]),
            'B=' + str(table[i][6]),
        ]
        if i > 0:
            features.extend([
                '-1:ismerged=' + str(table[i - 1][0]),
                '-1:ishead=' + str(table[i - 1][1]),
                '-1:isempty=' + str(table[i - 1][2]),
                '-1:isshorttext=' + str(table[i - 1][3]),
                '-1:islongtext=' + str(table[i - 1][4]),
                '-1:isnumeric=' + str(table[i - 1][5]),
                '-1:B=' + str(table[i - 1][6]),
            ])
        else:
            features.append('BOT')

        if i < len(table) - 1:
            features.extend([
                '+1:ismerged=' + str(table[i + 1][0]),
                '+1:ishead=' + str(table[i + 1][1]),
                '+1:isempty=' + str(table[i + 1][2]),
                '+1:isshorttext=' + str(table[i + 1][3]),
                '+1:islongtext=' + str(table[i + 1][4]),
                '+1:isnumeric=' + str(table[i + 1][5]),
                '+1:B=' + str(table[i + 1][6]),
            ])
        else:
            features.append('EOT')

        return features

    def table2features(self, table):
        return [self.row2features(table, i) for i in range(len(table))]

    def table2labels(self, table):
        return [label for ismerged, ishead, isempty, isshorttext, islongtext, isnumeric, bvalue, label in table]
    
    def print_transitions(self, trans_features):
        for (label_from, label_to), weight in trans_features:
            print("%-6s -> %-7s %0.6f" % (label_from, label_to, weight))

    def print_likely_trans(self, n):
        try:
            self.print_transitions(Counter(self.crf.transition_features_).most_common(n))
        except:
            print sys.exc_info()
            
    def print_unlikely_trans(self, n):
        try:
            self.print_state_features(Counter(self.crf.transition_features_).most_common()[-n:])
        except:
            print sys.exc_info()
    
    def print_state_features(self, state_features):
        for (attr, label), weight in state_features:
            print("%0.6f %-8s %s" % (weight, label, attr))
            
    def print_top_positive(self, n):
        try:
            self.print_state_features(Counter(self.crf.state_features_).most_common(n))
        except:
            print sys.exc_info()
            
    def print_top_negative(self, n):
        try:
            self.print_state_features(Counter(self.crf.state_features_).most_common()[-n:])
        except:
            print sys.exc_info()
    
    def buildModel(self, train_corpus, test_corpus, model_file):
        X_train = [self.table2features(s) for s in train_corpus]
        Y_train = [self.table2labels(s) for s in train_corpus]
        X_test = [self.table2features(s) for s in test_corpus]
        Y_test = [self.table2labels(s) for s in test_corpus]
        # TODO: set self.crf(model_filename='model')
        self.crf.fit(X_train, Y_train)
        pickle.dump(self.crf, open(model_file, 'wb'))
        labels = list(self.crf.classes_)
        print "LABELS %s" % labels
        y_pred = self.crf.predict(X_test)
        f1_score = metrics.flat_f1_score(Y_test, y_pred, average='weighted', labels=labels)
        seq_acc_score = metrics.sequence_accuracy_score(Y_test, y_pred)
        sorted_labels = sorted(labels)
        print(metrics.flat_classification_report(Y_test, y_pred, labels=sorted_labels, digits=3))
        return f1_score, seq_acc_score

    def buildModel2(self, X_train, Y_train, X_test, Y_test, model_file, c1, c2):
        self.crf.set_params(c1 = c1)
        self.crf.set_params(c2 = c2)
        self.crf.fit(X_train, Y_train)
        pickle.dump(self.crf, open(model_file, 'wb'))
        labels = list(self.crf.classes_)
        print "LABELS %s" % labels
        y_pred = self.crf.predict(X_test)
        f1_score = metrics.flat_f1_score(Y_test, y_pred, average='weighted', labels=labels)
        seq_acc_score = metrics.sequence_accuracy_score(Y_test, y_pred)
        sorted_labels = sorted(labels)
        print(metrics.flat_classification_report(Y_test, y_pred, labels=sorted_labels, digits=3))
        return f1_score, seq_acc_score
    
    def crossValidation(self, n, X_train, Y_train):
        # if __name__ == '__main__':
            # define fixed parameters and parameters to search, 3-folds cross validation
            # self.crf = sklearn_crfsuite.CRF(
            #     algorithm='lbfgs',
            #     max_iterations=100,
            #     all_possible_transitions=True
            # )
        params_space = {
            'c1': scipy.stats.expon(scale=0.5),
            'c2': scipy.stats.expon(scale=0.05),
        }
        self.crf.fit(X_train, Y_train)
        labels = list(self.crf.classes_)
        # use the same metric for evaluation
        f1_scorer = make_scorer(metrics.flat_f1_score,average='weighted', labels=labels)
        acc_scorer = make_scorer(metrics.flat_accuracy_score)
        prec_scorer = make_scorer(metrics.flat_f1_score)
        class_report = make_scorer(metrics.flat_classification_report)
        # search
    
        rs = RandomizedSearchCV(self.crf, params_space,
                                cv=n,
                                verbose=1,
                                n_jobs=-1,
                                n_iter=50,
                                scoring=f1_scorer
                                )
        rs.fit(X_train, Y_train)
        # print('grid scores:', rs.grid_scores_)
        print('best params:', rs.best_params_)
        print('best CV score:', rs.best_score_)
        print('model size: {:0.2f}M'.format(rs.best_estimator_.size_ / 1000000))
    # TODO: gimana caranya return grid scores, best params, best CV score? di luar block if atau di dalam?
        return rs.grid_scores_, rs.best_params_, rs.best_score_
        
    def predictAtable(self, test_corpus, model_file):
#       print len(test_corpus)
        X_test = [self.table2features(s) for s in test_corpus]
#         Y_test = [self.table2labels(s) for s in test_corpus]
#         print X_test
#         print Y_test
        #TODO: how to predict with model file
        model = pickle.load(open(model_file, 'rb'))
#         result = model.score(X_test, Y_test)
        y_pred = model.predict(X_test)
        # print y_pred
        return y_pred
#         print(result)
#         return result

    def testPredict(self, test_corpus, model_file):
        X_test = [self.table2features(s) for s in test_corpus]
        Y_test = [self.table2labels(s) for s in test_corpus]
        model = pickle.load(open(model_file, 'rb'))
        print "Model loaded %s" % model_file
        y_pred = model.predict(X_test)
        labels = list(model.classes_)
        f1_score = metrics.flat_f1_score(Y_test, y_pred, average='weighted', labels=labels)
        seq_acc_score = metrics.sequence_accuracy_score(Y_test, y_pred)
        sorted_labels = sorted(labels)
        print(metrics.flat_classification_report(Y_test, y_pred, labels=sorted_labels, digits=3))
        print(confusion_matrix(Y_test, y_pred))
        return f1_score, seq_acc_score