import numpy as np
import pandas as pd
import csv
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import Imputer

work_path = 'C:\\Users\Andrew\\Source\\Repos\\CollIntel\\Chapter 7\\'


def load_titanic(csv_file='train.csv'):
    AGE_INDEX = 3
    EMBARKED_INDEX = 7
    SEX_INDEX = 2

    df = pd.DataFrame.from_csv(work_path + csv_file)
    del df['Name']
    del df['Ticket']
    del df['Cabin']
    df = df[df['Embarked'].notnull()]
    arr = df.values

    # fill missing values for Age
    x = np.transpose([arr[:, AGE_INDEX]])
    imp = Imputer(missing_values='NaN', strategy='median', copy=True)
    x = imp.fit_transform(x)
    arr[:, AGE_INDEX] = x[:, 0]

    # vectorize sex and embarked
    dicts = []
    for row in arr[:, [SEX_INDEX, EMBARKED_INDEX]]:
        dicts.append({'sex': row[0], 'embarked': row[1]})
    arr = np.delete(arr, [SEX_INDEX, EMBARKED_INDEX], 1)
    vec = DictVectorizer()
    vect_dicts = vec.fit_transform(dicts).toarray()
    arr = np.c_[arr, vect_dicts]

    return arr


def load_submit_titanic(csv_file='test.csv'):
    AGE_INDEX = 2
    FARE_INDEX = 5
    EMBARKED_INDEX = 6
    SEX_INDEX = 1

    df = pd.DataFrame.from_csv(work_path + csv_file)
    del df['Name']
    del df['Ticket']
    del df['Cabin']
    arr = df.values

    # fill missing values for Age
    x = arr[:, [AGE_INDEX, FARE_INDEX]]
    imp = Imputer(missing_values='NaN', strategy='median', copy=True)
    x = imp.fit_transform(x)
    arr[:, AGE_INDEX] = x[:, 0]
    arr[:, FARE_INDEX] = x[:, 1]

    # vectorize sex and embarked
    dicts = []
    for row in arr[:, [SEX_INDEX, EMBARKED_INDEX]]:
        dicts.append({'sex': row[0], 'embarked': row[1]})
    arr = np.delete(arr, [SEX_INDEX, EMBARKED_INDEX], 1)
    vec = DictVectorizer()
    vect_dicts = vec.fit_transform(dicts).toarray()
    arr = np.c_[arr, vect_dicts]

    return arr


def build_submit_data(y, csv_file='test.csv'):
    with open(work_path + 'test.csv', 'rb') as csvfile_input:
        reader = csv.reader(csvfile_input)
        # skip header
        reader.next()
        with open(work_path + 'submit.csv', 'wb') as csvfile_output:
            writer = csv.writer(csvfile_output)
            writer.writerow(['PassengerId', 'Survived'])
            index = 0
            for row in reader:
                writer.writerow([row[0], y[index]])
                index += 1



def run_decision_tree(train_data, test_data, submit_data=None):
    dt = DecisionTreeClassifier(criterion='gini',
                                splitter='best',
                                max_features=None,
                                random_state=1,
                                min_samples_leaf=3)

    y_train = train_data[:, 0].astype(int)
    X_train = train_data[:, 1:].astype(int)

    dt.fit(X_train, y_train)

    y = test_data[:, 0].astype(int)
    X = test_data[:, 1:].astype(int)
    print 'Accuracy (train): ', dt.score(X_train, y_train)
    print 'Accuracy (test): ', dt.score(X, y)
    print 'Classes', dt.n_classes_
    print 'Classes', dt.classes_
    print '#Features', dt.n_features_
    print 'Max features', dt.max_features
    print 'Feature importances', dt.feature_importances_
    print 'Tree capacity', dt.tree_.capacity

    if submit_data is not None:
        ys = dt.predict(submit_data.astype(int))
        build_submit_data(ys)


#load train data
X = load_titanic()
X_shape = np.shape(X)

# split data set
n_sample = X_shape[0]
latest = int(n_sample * 0.7)
train_data = X[0:latest, :]
test_data = X[latest:, :]

# Load submition data
# X_submit = None
X_submit = load_submit_titanic()

run_decision_tree(train_data, test_data, X_submit)



