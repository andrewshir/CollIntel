from sklearn.neighbors import KNeighborsClassifier
from sklearn.cross_validation import KFold, cross_val_score
from sklearn.preprocessing import scale
import pandas as pd
import numpy as np


working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week2\\"
df = pd.read_csv(filepath_or_buffer=working_path + "wine.data", header=None)

# print DataFrame and its shape
# print df
# print df.shape
#
X = df.iloc[:, 1:]
y = df.iloc[:, 0]

# print sets as Pandas objects
# print X
# print y

# print sets as Numpy objects
# print X.as_matrix()
# print y.as_matrix()

X = X.as_matrix()
y = y.as_matrix()

# fold generator
kfold = KFold(len(y), 5, shuffle=True, random_state=42)

# feature scaling
X = scale(X)

# train classifier
max = 0
max_k = 0
for k in xrange(1, 51):
    knn = KNeighborsClassifier(n_neighbors=k)
    scores = cross_val_score(knn, X=X, y=y, cv=kfold)
    score = np.average(scores)

    if max < score:
        max = score
        max_k = k
    print k, score

print "Max:", max_k, max

# answer: 1 0.73
# answer: 29 0.98

