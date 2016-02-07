import pandas as pd
from sklearn.preprocessing import StandardScaler, scale
from sklearn.linear_model import Perceptron
import numpy as np

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week2\\"
df = pd.read_csv(filepath_or_buffer=working_path + "perceptron-train.csv", header=None)

X = df.iloc[:, 1:]
y = df.iloc[:, 0]

X = X.as_matrix()
y = y.as_matrix()

df = pd.read_csv(filepath_or_buffer=working_path + "perceptron-test.csv", header=None)
X_test = df.iloc[:, 1:]
y_test = df.iloc[:, 0]

X_test = X_test.as_matrix()
y_test = y_test.as_matrix()

p = Perceptron(random_state=241)
p.fit(X, y)
correctness = p.predict(X_test) == y_test
print "Without scaling"
print "Accuracy", float(np.sum(correctness))/len(correctness)

# scale function will not worl actually because we need to calculate scaling factors on training set and use them
# for testing set, which is not possible with single scale function
# X = scale(X)
# X_test = scale(X_test)

scaler = StandardScaler()
X = scaler.fit_transform(X)
X_test = scaler.transform(X_test)


p = Perceptron(random_state=241)
p.fit(X, y)
correctness = p.predict(X_test) == y_test
print "With scaling"
print "Accuracy", float(np.sum(correctness))/len(correctness)


