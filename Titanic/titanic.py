import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.cross_validation import KFold
from sklearn.cross_validation import cross_val_score
from sklearn.grid_search import GridSearchCV

working_dir = r'C:\Users\Andrew\Source\Repos\CollIntel\Titanic'


def write_data(index, prediced):
    df = pd.DataFrame({'Survived': prediced}, index=index)
    df.to_csv(working_dir + r'\out\test_predicted.csv')


def read_data():
    # train dataset with right class labels
    train = pd.read_csv(working_dir + r'\train.csv', index_col='PassengerId')
    # test dataset
    test = pd.read_csv(working_dir + r'\test.csv', index_col='PassengerId')
    # dataset with all objects
    all = pd.concat([train, test])
    del all['Survived']
    return train, test, all


def build_features(df):
    def get_title(name):
        if 'Mr.' in name:
            return 1
        elif 'Don.' in name:
            return 1
        elif 'Dr.' in name:
            return 1
        elif 'Col.' in name:
            return 1
        elif 'Sir.' in name:
            return 1
        elif 'Rev.' in name:
            return 1
        elif 'Jonkheer.' in name:
            return 1
        elif 'Capt.' in name:
            return 1
        elif 'Major.' in name:
            return 1
        elif 'Mrs.' in name:
            return 2
        elif 'Mme.' in name:
            return 2
        elif 'Lady.' in name:
            return 2
        elif 'Mlle.' in name:
            return 2
        elif 'Countess.' in name:
            return 2
        elif 'Ms.' in name:
            return 2
        elif'Dona.' in name:
            return 2
        elif 'Master.' in name:
            return 3
        elif 'Miss.' in name:
            return 4
        return 0

    def get_family_number(name, dict):
        if ',' not in name:
            return 0
        surname = name[0:name.index(',')]
        if surname in dict:
            return dict[surname]
        else:
            return 0

    del df['Embarked']
    del df['Ticket']
    del df['Cabin']
    df.ix[:, 'Sex'] = df.ix[:, 'Sex'].map(lambda x: 1 if x == 'male' else 0)
    df.ix[:, 'Title'] = df.ix[:, 'Name'].map(lambda x: get_title(x))

    names = {}
    for name in df['Name'].values:
        if ',' not in name:
            continue
        surname = name[0:name.index(',')]
        names.setdefault(surname, 0)
        names[surname] += 1

    df.ix[:, 'Cofam'] = df.ix[:, 'Name'].map(lambda x: get_family_number(x, names))
    del df['Name']
    df['ParchSibSp'] = df['SibSp'] + df['Parch']
    df['ParchSibSpCofam'] = df['SibSp'] + df['Parch'] + df['Cofam']


def fill_missing_values(df):
    df['Fare'].fillna(df['Fare'].mean(), inplace=True)
    df['Age'].fillna(30, inplace=True)


def define_features_importance(X, y, features):
    clf = RandomForestClassifier(n_estimators=1000, random_state=241)
    clf.fit(X, y)
    rating = []
    for i in xrange(len(features)):
        rating.append((features[i], clf.feature_importances_[i]))
    rating.sort(key=lambda x: x[1], reverse=True)
    for pair in rating:
        print pair[0], '=', pair[1]


def get_X_y(df):
    dfc = df.copy()
    if 'Survived' in dfc:
        del dfc['Survived']
    X = dfc.as_matrix()
    y = None
    if 'Survived' in dfc:
        y = df['Survived'].values
    return X, y, dfc.columns


df_train, df_test, df_all = read_data()
build_features(df_train)
fill_missing_values(df_train)

X, y, columns = get_X_y(df_train)
define_features_importance(X, y, columns.values)

clf = GradientBoostingClassifier(learning_rate=0.01, n_estimators=260, max_depth=2, random_state=1)
kfold = KFold(n=X.shape[0], n_folds=5, random_state=241, shuffle=True)
scores = cross_val_score(clf, X, y, cv=kfold, scoring='accuracy')
print "Scores:"
print "mean=", scores.mean()
print "min=", scores.min()
print "max=", scores.max()


clf = GradientBoostingClassifier(random_state=158)
parameters = {'n_estimators': range(50, 500, 30), 'max_depth': [2, 3, 4, 5]}
gs = GridSearchCV(clf, param_grid=parameters, scoring='accuracy')
gs.fit(X, y)
for p, mean_score, cv_score in gs.grid_scores_:
    print mean_score, p


build_features(df_test)
fill_missing_values(df_test)
clf = GradientBoostingClassifier(learning_rate=0.01, n_estimators=260, max_depth=2, random_state=1)
clf.fit(X, y)
X_test, y_test = get_X_y(df_test)
predicted = clf.predict(X_test)
write_data(df_test.index, predicted)
