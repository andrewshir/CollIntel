import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import log_loss
import matplotlib.pyplot as plt
import numpy as np

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week5\\"
df = pd.read_csv(filepath_or_buffer=working_path + "gbm-data.csv")

X = df.iloc[:, 1:].as_matrix()
y = df.iloc[:, 0].as_matrix()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8, random_state=241)

for l in [1, 0.5, 0.3, 0.2, 0.1]:
    cf = GradientBoostingClassifier(n_estimators=250,
                                    verbose=True, random_state=241, learning_rate=l)
    cf.fit(X_train, y_train)

    train_loss = []
    test_loss = []

    # log loss for train set
    for stage, array in enumerate(cf.staged_decision_function(X_train)):
        # apply sigmoid function
        transformed = []
        for row in array:
            transformed.append(float(1) / (1+np.exp(-row[0])))
        # calculate metric
        score = log_loss(y_train, transformed)
        train_loss.append(score)

    # log loss for test set
    for stage, array in enumerate(cf.staged_decision_function(X_test)):
            # apply sigmoid function
            transformed = []
            for row in array:
                transformed.append(float(1) / (1+np.exp(-row[0])))
            # calculate metric
            score = log_loss(y_test, transformed)
            test_loss.append(score)

    min_val = np.min(test_loss)
    min_stage = np.argmin(test_loss)
    print "l=", l, "test_loss=", test_loss
    print "min=", min_val
    print "min-stage=", min_stage

    plt.figure()
    plt.plot(test_loss, 'r', linewidth=2)
    plt.plot(train_loss, 'g', linewidth=2)
    plt.legend(['test', 'train'])
    plt.show()



