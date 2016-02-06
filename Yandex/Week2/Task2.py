from sklearn.neighbors import KNeighborsRegressor
from sklearn.cross_validation import KFold, cross_val_score
from sklearn.preprocessing import scale
import pandas as pd
import numpy as np
from sklearn.datasets import load_boston

dataset = load_boston()

# print training set
# print dataset.data.shape
# print dataset.data
# print dataset.target

X = dataset.data
y = dataset.target

X = scale(X)

p_space = np.linspace(1, 10, 200)
kfold = KFold(len(y), 5, shuffle=True, random_state=42)
max = -100
max_p = 0

for p in p_space:
    knn = KNeighborsRegressor(weights='distance', metric='minkowski', p=p)
    scores = cross_val_score(knn, X=X, y=y, cv=kfold, scoring='mean_squared_error')
    score = np.max(scores)

    if max < score:
        max = score
        max_p = p
    print p, score

print "Max", max_p, max

# answer 1.13567839196




