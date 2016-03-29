import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.cross_validation import KFold
from sklearn.cross_validation import cross_val_score
from sklearn.grid_search import GridSearchCV

working_dir = r'C:\Users\Andrew\Source\Repos\CollIntel\Titanic'


def write_data(index, predicted, show_diff=True):
    predicted = [int(x) for x in predicted]
    df = pd.DataFrame({'Survived': predicted}, index=index)
    df.to_csv(working_dir + r'\out\test_predicted.csv')
    if show_diff:
        df_test = pd.read_csv(working_dir + r'\test.csv', index_col='PassengerId')
        df_eth = pd.read_csv(working_dir + r'\out\test_predicted.csv', index_col='PassengerId')
        df_pred = pd.read_csv(working_dir + r'\out\test_ethalon.csv', index_col='PassengerId')
        df_test['Survived'] = df_pred['Survived']
        df_pred = df_test
        print_diff(df_pred, df_eth)


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

    def get_city_code(city):
        if city == 'Q':
            return 1
        elif city == 'S':
            return 2
        elif city == 'C':
            return 3
        return 2

    def get_cabin_count(cabin):
        if isinstance(cabin, basestring):
            return len(cabin.split(' '))
        return 0

    del df['Ticket']
    del df['Cabin']
    # del df['Age']
    del df['Embarked']
    # df.ix[:, 'Embarked'] = df.ix[:, 'Embarked'].map(get_city_code)
    # df.ix[:, 'Cabin'] = df.ix[:, 'Cabin'].map(get_cabin_count)
    df.ix[:, 'Sex'] = df.ix[:, 'Sex'].map(lambda x: 1 if x == 'male' else 0)
    df.ix[:, 'Title'] = df.ix[:, 'Name'].map(get_title)

    names = {}
    for name in df['Name'].values:
        if ',' not in name:
            continue
        surname = name[0:name.index(',')]
        names.setdefault(surname, 0)
        names[surname] += 1

    # df.ix[:, 'Cofam'] = df.ix[:, 'Name'].map(lambda x: get_family_number(x, names))
    del df['Name']
    # df['ParchSibSp'] = df['SibSp'] + df['Parch']
    # df['ParchSibSpCofam'] = df['SibSp'] + df['Parch'] + df['Cofam']


def fill_missing_values(df, df_all):
    df['Fare'].fillna(df['Fare'].mean(), inplace=True)
    # df['Embarked'].fillna(df['Embarked'].median(), inplace=True)

    # fill age with some constant
    df['Age'].fillna(30, inplace=True)

    # fill age calculated values
    # age_train = df_all.loc[df_all['Age'].notnull()].copy()
    # age_train['Fare'].fillna(age_train['Fare'].mean(), inplace=True)
    # age_test = df_all.loc[df_all['Age'].isnull()].copy()
    # age_test['Fare'].fillna(age_test['Fare'].mean(), inplace=True)
    # reg = GradientBoostingRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
    # reg.fit(age_train.iloc[:, 1:].as_matrix(), age_train.iloc[:, 0].as_matrix())
    # age_test.iloc[:, 0] = reg.predict(age_test.iloc[:, 1:].as_matrix())
    # dataset = pd.concat([age_train, age_test])
    # df.update(dataset['Age'])


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
    if 'Survived' in dfc.columns:
        del dfc['Survived']
    X = dfc.as_matrix()
    y = None
    if 'Survived' in df.columns:
        y = df['Survived'].values
    return X, y, dfc.columns


def print_diff(df1, df2):
    diff = df1.loc[df1['Survived'] != df2['Survived'], :]
    if diff.shape[0] > 0:
        print "This rows have diff (original predicted values shown):"
        print diff
    else:
        print "*** No difference found"


def build_error_table(df, row, col):
    row_values = df[row].unique()
    row_values.sort()
    col_values = df[col].unique()
    col_values.sort()

    print '|%10s|' % col,
    for cv in col_values:
        print '%5s|' % cv,
    print

    print '|%10s|' % row,
    for cv in col_values:
        print '-----|' % cv,
    print

    for rv in row_values:
        print '|%10s|' % rv,
        for cv in col_values:
            df_filt = df.loc[df[row] == rv, :].loc[df[col] == cv, :]
            errors_count = df_filt[df_filt['Survived'] == df_filt['SurvivedPred']].shape[0]
            total_count = df_filt.shape[0]
            error_rate = 0 if total_count == 0 else float(errors_count) / total_count
            print ' %0.2f|' % error_rate,
        print


def manual_decision_tree(X):
    cn_pclass = 0
    cn_sex = 1
    cn_age = 2
    cn_sibsp = 3
    cn_parch = 4
    cn_fare = 5
    cn_title = 6

    y = []
    for row in X:
        if row[cn_sex] == 0:
            if row[cn_pclass] < 3:
                y.append(1)
            else:
                if row[cn_age] < 6:
                    y.append(1)
                else:
                    if row[cn_fare] < 9:
                        y.append(1)
                    else:
                        if 24 <= row[cn_age] <= 36 and 11 <= row[cn_fare] <= 21:
                            y.append(1)
                        else:
                            y.append(0)
        else:
            if row[cn_pclass] > 1:
                y.append(0)
            else:
                if row[cn_fare] > 300:
                    y.append(1)
                else:
                    if row[cn_age] < 17:
                        y.append(1)
                    else:
                        y.append(0)
    return y

df_train, df_test, df_all = read_data()
build_features(df_train)
build_features(df_test)
build_features(df_all)
fill_missing_values(df_train, df_all)
fill_missing_values(df_test, df_all)

X, y, columns = get_X_y(df_train)
# define_features_importance(X, y, columns.values)

# run grid search for optimal parameters
# clf = GradientBoostingClassifier(random_state=1)
# parameters = {'n_estimators': range(50, 500, 30), 'max_depth': [2, 3, 4, 5]}
# gs = GridSearchCV(clf, param_grid=parameters, scoring='accuracy')
# gs.fit(X, y)
# scores = []
# scores.extend(gs.grid_scores_)
# scores.sort(key=lambda x: x[1], reverse=True)
# for p, mean_score, cv_score in scores:
#     print mean_score, p


# create classifier with optimal parameters
clf = GradientBoostingClassifier(learning_rate=0.01, n_estimators=260, max_depth=2, random_state=1)

# build error table on trained dataset
# clf.fit(X, y)
# predicted = clf.predict(X)
# dft = df_train.copy()
# dft['SurvivedPred'] = predicted
# build_error_table(dft, row='Sex', col='Pclass')

# build error table for manual decision tree
# predicted = manual_decision_tree(X)
# dft = df_train.copy()
# dft['SurvivedPred'] = predicted
# build_error_table(dft, row='Sex', col='Pclass')

# run classifier cross_validation
# kfold = KFold(n=X.shape[0], n_folds=5, random_state=241, shuffle=True)
# scores = cross_val_score(clf, X, y, cv=kfold, scoring='accuracy')
# print "Scores:"
# print "mean=", scores.mean()
# print "min=", scores.min()
# print "max=", scores.max()

# run on test data
# clf.fit(X, y)
# X_test, y_test, columns = get_X_y(df_test)
# predicted = clf.predict(X_test)
# write_data(df_test.index, predicted)

# run data manual tree on test data
# X_test, y_test, columns = get_X_y(df_test)
# predicted = manual_decision_tree(X_test)
# write_data(df_test.index, predicted)

