import pandas as pd
import math
from sklearn.metrics import roc_auc_score

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week3\\"
df = pd.read_csv(filepath_or_buffer=working_path + "data-logistic.csv", header=None)

X = df.iloc[:, 1:]
y = df.iloc[:, 0]

X = X.as_matrix()
y = y.as_matrix()

w1 = 1
w2 = 1


def descent(w1, w2, k, l, C):
    sigm1 = 0
    sigm2 = 0
    for i,(x1,x2) in enumerate(X):
        sigm1 += y[i] * x1 * (1 - 1 / (1 + math.exp(-y[i]*(w1*x1 + w2*x2))))
        sigm2 += y[i] * x2 * (1 - 1 / (1 + math.exp(-y[i]*(w1*x1 + w2*x2))))

    # without regularization
    # w1 = w1 + k / l * sigm1
    # w2 = w2 + k / l * sigm2

    # with regularization
    w1 = w1 + k / l * sigm1 - k * C * w1
    w2 = w2 + k / l * sigm2 - k * C * w2

    return w1, w2

def prob_estimation(w1, w2, X):
    print "w1=", w1
    print "w2=", w2

    result = []
    for x1, x2 in X:
        a = 1 / (1 + math.exp(-w1*x1 - w2 * x2))
        result.append(a)
    return result


def run(w1,w2):
    k = 0.1
    xi = 0.00001
    l = len(y)
    C = 10

    for i in xrange(10000):
        w1_new, w2_new = descent(w1, w2, k, l, C)

        if math.fabs(w1-w1_new) < xi and math.fabs(w2-w2_new) < xi:
            break
        else:
            w1 = w1_new
            w2 = w2_new

    print "i", i
    print "w1", w1
    print "w2", w2


def auc_roc():
    # with regularization
    # w1 = 0.029
    # w2 = 0.025

    # without regularization
    w1 = 0.288
    w2 = 0.092

    pe = prob_estimation(w1, w2, X)
    # print len(y)
    # print y
    # print len(pe)
    # print pe

    print "roc_auc", roc_auc_score(y, pe)

# auc_roc()
run(w1, w2)