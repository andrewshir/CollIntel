import pandas as pd
from sklearn import datasets
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.cross_validation import KFold
from sklearn.grid_search import GridSearchCV
import numpy as np
import itertools
import math

# build features and class labels
newsgroups = datasets.fetch_20newsgroups(subset='all', categories=['alt.atheism', 'sci.space'])
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(newsgroups.data)
y = newsgroups.target

# find C parameter
# grid = {'C': np.power(10, np.arange(-5.0, 6.0, step=1.0))}
# cv = KFold(y.size, n_folds=5, shuffle=True, random_state=241)
# svc = SVC(kernel='linear', random_state=241)
# gs = GridSearchCV(svc, grid, scoring='accuracy', cv=cv)
# gs.fit(X, y)
#
# for a in gs.grid_scores_:
#     print a.parameters
#     print a.mean_validation_score

# build SVC with optimal parameter
svc = SVC(kernel='linear', random_state=241, C=1)
svc.fit(X, y)


def wrong_method():
    # get support vectors
    sv = svc.support_vectors_

    # convert to COO sparse matrix format to use col row
    sv_csr = sv
    sv = sv.tocoo()


    elems = []
    for i, j, v in itertools.izip(sv.row, sv.col, sv.data):
        if len(elems) < 10 or elems[0][0] < math.fabs(v):
            elems.append((math.fabs(v), i, j))
            elems.sort(key=lambda x: x[0])
            while len(elems) > 10:
                del elems[0]

    words = vectorizer.get_feature_names()
    print "Top 10 words"
    topwords = []
    for el in elems:
        row = el[1]
        col = el[2]
        word = words[col]
        topwords.append(word)
        print "weight=", el[0], " row=", row, " col=", col, " [", word, "]",\
            " Self-check=", \
            sv_csr[row, col], " ", ("passed" if sv_csr[row, col] == el[0] else "ERROR")
    print

    topwords.sort()
    print "Sorted top words"
    print topwords

fw = svc.coef_.tocoo()
elems = []
for i, j, v in itertools.izip(fw.row, fw.col, fw.data):
    if len(elems) < 10 or elems[0][0] < math.fabs(v):
        elems.append((math.fabs(v), i, j))
        elems.sort(key=lambda x: x[0])
        while len(elems) > 10:
            del elems[0]

words = vectorizer.get_feature_names()
print "Top 10 words"
topwords = []
for el in elems:
    row = el[1]
    col = el[2]
    word = words[col]
    topwords.append(word)
    print "weight=", el[0], " row=", row, " col=", col, " [", word, "]",\
        " Self-check=", \
        svc.coef_[row, col], " ", ("passed" if math.fabs(svc.coef_[row, col]) == el[0] else "ERROR")
print

topwords.sort()
print "Sorted top words"
print topwords






