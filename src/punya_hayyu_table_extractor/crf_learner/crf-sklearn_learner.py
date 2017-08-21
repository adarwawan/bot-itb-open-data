## USE sklearn_crfsuite

from itertools import chain
import nltk
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn
import pycrfsuite
import string
from sklearn.metrics import make_scorer
from sklearn.cross_validation import cross_val_score
from sklearn.grid_search import RandomizedSearchCV
import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
import scipy
from collections import Counter

infile = "train.txt"
with open(infile, "rb") as table:
    data = table.readlines()

corpus = []
element = []
for i in range(len(data)):
    if len(data[i]) > 2:
        element.append(data[i])
    else:
        corpus.append(element)
        element = []

ready_corpus = []
for j in range(len(corpus)):
    tmp_corpus = []
    for k in range(len(corpus[j])):
        temp = string.rstrip(corpus[j][k], '\r\n')
        to_list = temp.split(",")
        tmp_corpus.append(to_list)
    ready_corpus.append(tmp_corpus)

infile2 = "test.txt"
with open(infile2, "rb") as table2:
    data2 = table2.readlines()

corpus2 = []
element2 = []
for i in range(len(data2)):
    if len(data2[i]) > 2:
        element2.append(data2[i])
    else:
        corpus2.append(element2)
        element2 = []

ready_corpus2 = []
for j in range(len(corpus2)):
    tmp_corpus2 = []
    for k in range(len(corpus2[j])):
        temp2 = string.rstrip(corpus2[j][k], '\r\n')
        to_list2 = temp2.split(",")
        tmp_corpus2.append(to_list2)
    ready_corpus2.append(tmp_corpus2)

# print ready_corpus[0]
# print ready_corpus[1]
train_data = ready_corpus
test_data = ready_corpus2

def row2features(table, i):
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


def table2features(table):
    return [row2features(table, i) for i in range(len(table))]


def table2labels(table):
    return [label for ismerged, ishead, isempty, isshorttext, islongtext, isnumeric, bvalue, label in table]


# def sent2tokens(sent):
#     return [ismerged, ishead, isempty, isshorttext, islongtext, isnumeric, bvalue for ismerged, ishead, isempty, isshorttext, islongtext, isnumeric, bvalue, label in sent]

# sent2features(ready_corpus[0])
# sent2labels(ready_corpus[0])

X_train = [table2features(s) for s in train_data]
Y_train = [table2labels(s) for s in train_data]
X_test = [table2features(s) for s in test_data]
Y_test = [table2labels(s) for s in test_data]

crf = sklearn_crfsuite.CRF(
    algorithm='lbfgs',
    c1=0.0066,
    c2=0.1777,
    max_iterations=500,
    all_possible_transitions=True,
    model_filename='c3_bps-itb500it.crfsuite'
)
crf.fit(X_train, Y_train)
labels = list(crf.classes_)
print "LABELS %s" % labels
y_pred = crf.predict(X_test)

metrics.flat_f1_score(Y_test, y_pred, average='weighted', labels=labels)

sorted_labels = sorted(labels)
print(metrics.flat_classification_report(Y_test, y_pred, labels=sorted_labels, digits=3))

def print_transitions(trans_features):
    for (label_from, label_to), weight in trans_features:
        print("%-6s -> %-7s %0.6f" % (label_from, label_to, weight))

print("Top likely transitions:")
print_transitions(Counter(crf.transition_features_).most_common(20))
print("\nTop unlikely transitions:")
print_transitions(Counter(crf.transition_features_).most_common()[-20:])

def print_state_features(state_features):
    for (attr, label), weight in state_features:
        print("%0.6f %-8s %s" % (weight, label, attr))

print("Top positive:")
print_state_features(Counter(crf.state_features_).most_common(30))

print("\nTop negative:")
print_state_features(Counter(crf.state_features_).most_common()[-30:])

# if __name__ == '__main__':
#     # define fixed parameters and parameters to search, 3-folds cross validation
#     crf = sklearn_crfsuite.CRF(
#         algorithm='lbfgs',
#         max_iterations=100,
#         all_possible_transitions=True
#     )
#     params_space = {
#         'c1': scipy.stats.expon(scale=0.5),
#         'c2': scipy.stats.expon(scale=0.05),
#     }
#     crf.fit(X_train, Y_train)
#     labels = list(crf.classes_)
#     # use the same metric for evaluation
#     f1_scorer = make_scorer(metrics.flat_f1_score,average='weighted', labels=labels)
#     acc_scorer = make_scorer(metrics.flat_accuracy_score)
#     prec_scorer = make_scorer(metrics.flat_f1_score)
#     class_report = make_scorer(metrics.flat_classification_report)
#     # search
#
#     rs = RandomizedSearchCV(crf, params_space,
#                             cv=10,
#                             verbose=1,
#                             n_jobs=-1,
#                             n_iter=50,
#                             scoring=f1_scorer
#                             )
#     rs.fit(X_train, Y_train)
#     print('grid scores:', rs.grid_scores_)
#     print('best params:', rs.best_params_)
#     print('best CV score:', rs.best_score_)
#     print('model size: {:0.2f}M'.format(rs.best_estimator_.size_ / 1000000))
