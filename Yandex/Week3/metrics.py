import pandas as pd
import sklearn.metrics as metrics
import numpy as np

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week3\\"
df = pd.read_csv(filepath_or_buffer=working_path + "classification.csv")

y_true = df.iloc[:, 0].as_matrix()
y_pred = df.iloc[:, 1].as_matrix()

def calculate_metric():
    tp = 0
    fp = 0
    fn = 0
    tn = 0
    for i, y in enumerate(y_true):
        yp = y_pred[i]
        if y == 1:
            if y == yp:
                tp += 1
            else:
                fn += 1
        else:
            if y == yp:
                tn += 1
            else:
                fp += 1

    return tp, fp, fn, tn

def get_prec(y_pred):
    precision, recall, thresholds = metrics.precision_recall_curve(y_true, y_pred)

    idx = 0
    for i, r in enumerate(recall):
        if r < 0.7:
            idx = i
            break

    return np.max(precision[0:idx])


print calculate_metric()
print len(y_true)
print "accuracy_score", metrics.accuracy_score(y_true, y_pred)
print "precision_score", metrics.precision_score(y_true, y_pred)
print "recall_score", metrics.recall_score(y_true, y_pred)
print "f1_score", metrics.f1_score(y_true, y_pred)
print

df = pd.read_csv(filepath_or_buffer=working_path + "scores.csv")
y_true = df.iloc[:, 0].as_matrix()
logreg = df.iloc[:, 1].as_matrix()
svm = df.iloc[:, 2].as_matrix()
knn = df.iloc[:, 3].as_matrix()
tree = df.iloc[:, 4].as_matrix()

print "logreg=", metrics.roc_auc_score(y_true, logreg)
print "svm=", metrics.roc_auc_score(y_true, svm)
print "knn=", metrics.roc_auc_score(y_true, knn)
print "tree=", metrics.roc_auc_score(y_true, tree)
print


print "logreg=", get_prec(logreg)
print "svm=", get_prec(svm)
print "knn=", get_prec(knn)
print "tree=", get_prec(tree)
print




