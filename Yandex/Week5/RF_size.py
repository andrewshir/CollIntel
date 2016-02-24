import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import KFold
from sklearn.metrics import r2_score


def scorer(estimator, X, y):
    y_pred = estimator.predict(X)
    return r2_score(y, y_pred)


working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week5\\"
df = pd.read_csv(filepath_or_buffer=working_path + "abalone.csv")
df['Sex'] = df['Sex'].map(lambda x: 1 if x == 'M' else (-1 if x == 'F' else 0))

X = df.iloc[:, 0:-1].as_matrix()
y = df.iloc[:, -1].as_matrix()

fold = KFold(n=len(y), n_folds=5, shuffle=True, random_state=1)

for k in xrange(1, 51):
    cf = RandomForestRegressor(n_estimators=k, random_state=1)
    scores = cross_val_score(cf, X, y, scoring='r2', cv=fold)
    print "k=", k, " score=", np.mean(scores)