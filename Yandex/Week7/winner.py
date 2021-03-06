# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.cross_validation import KFold
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.grid_search import GridSearchCV
import datetime


working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week7\\"

# 1. Считайте таблицу с признаками из файла features.csv с помощью кода, приведенного выше.
# Удалите признаки, связанные с итогами матча (они помечены в описании данных как отсутствующие в тестовой выборке).

train_df = pd.read_csv(working_path + "features.csv", index_col='match_id')
del train_df['duration']
del train_df['tower_status_radiant']
del train_df['tower_status_dire']
del train_df['barracks_status_radiant']
del train_df['barracks_status_dire']
del train_df['start_time']
# radiant_win будет удален дальше после формирования вектора y

# 2. Проверьте выборку на наличие пропусков с помощью функции count(), которая для каждого столбца показывает
# число заполненных значений. Много ли пропусков в данных?
# Запишите названия признаков, имеющих пропуски, и попробуйте для любых двух из них дать обоснование,
# почему их значения могут быть пропущены.
row_count = train_df.shape[0]
counts = train_df.count()
print "Columns with missed values (total %s rows):" % row_count
print counts[counts < row_count]
print

# 3. Замените пропуски на нули с помощью функции fillna().
train_df = train_df.fillna(0)

# 4. Какой столбец содержит целевую переменную? Запишите его название.
y = train_df['radiant_win'].as_matrix()
del train_df['radiant_win']

# 5. Забудем, что в выборке есть категориальные признаки, и попробуем обучить градиентный бустинг над деревьями на
# имеющейся матрице "объекты-признаки".
kfold = KFold(n=row_count, n_folds=5, shuffle=True, random_state=123)


# Оцените качество градиентного бустинга (GradientBoostingClassifier) с помощью данной кросс-валидации,
# попробуйте при этом разное количество деревьев
def exec_gradient_boosting():
    print '*' * 80
    print ' ' * 20, 'APPROACH A: GRADIENT BOOSTING'
    print '*' * 80

    X = train_df.as_matrix()
    tuned_params = {'n_estimators': range(5, 41, 5),
                    'learning_rate': [0.1, 0.5, 1.0],
                    'max_depth': [2, 3]}

    cf = GradientBoostingClassifier()
    gs = GridSearchCV(estimator=cf,
                      param_grid=tuned_params,
                      cv=kfold,
                      scoring='roc_auc')

    start_time = datetime.datetime.now()
    gs.fit(X, y)
    time_elapsed = datetime.datetime.now() - start_time
    print "Best hyper-parameter values:"
    print gs.best_params_
    print
    print "Grid scores on development set:"
    for params, mean_score, scores in gs.grid_scores_:
        print("%0.6f (+/-%0.03f) for %r"
              % (mean_score, scores.std() * 2, params))
    print "Time elapsed: %s" % time_elapsed
    print

exec_gradient_boosting()


# 1. Оцените качество логистической регрессии (sklearn.linear_model.LogisticRegression с L2-регуляризацией)
# с помощью кросс-валидации по той же схеме, которая использовалась для градиентного бустинга. Подберите при этом
# лучший параметр регуляризации (C).
train_df_log = train_df.copy()

def exec_logistic_regression(subtitle=''):
    print '*' * 80
    print ' ' * 20, 'APPROACH B: LOGISTIC REGRESSION %s' % subtitle
    print '*' * 80

    X_log = train_df_log.as_matrix()
    scaler = StandardScaler()
    X = scaler.fit_transform(X=X_log)

    tuned_params = {'C': [0.001, 0.003, 0.005, 0.01, 0.1, 0.5, 1.0, 1.5, 5.0]}
    cf = LogisticRegression(penalty='l2')
    gs = GridSearchCV(estimator=cf,
                      param_grid=tuned_params,
                      cv=kfold,
                      scoring='roc_auc')

    start_time = datetime.datetime.now()
    gs.fit(X, y)
    time_elapsed = datetime.datetime.now() - start_time
    print "Best hyper-parameter values:"
    print gs.best_params_
    print
    print "Grid scores on development set:"
    for params, mean_score, scores in gs.grid_scores_:
        print("%0.6f (+/-%0.03f) for %r"
              % (mean_score, scores.std() * 2, params))
    print "Time elapsed: %s" % time_elapsed
    print

exec_logistic_regression()


# 2. Среди признаков в выборке есть категориальные, которые мы использовали как числовые,
#  что вряд ли является хорошей идеей. Категориальных признаков в этой задаче одиннадцать:
# lobby_type и r1_hero, r2_hero, ..., r5_hero, d1_hero, d2_hero, ..., d5_hero.
# Уберите их из выборки, и проведите кросс-валидацию для логистической регрессии на новой выборке с подбором
# лучшего параметра регуляризации.
def remove_categorial_features(df):
    del df['lobby_type']
    del df['r1_hero']
    del df['r2_hero']
    del df['r3_hero']
    del df['r4_hero']
    del df['r5_hero']
    del df['d1_hero']
    del df['d2_hero']
    del df['d3_hero']
    del df['d4_hero']
    del df['d5_hero']

remove_categorial_features(train_df_log)
exec_logistic_regression(subtitle='W/O CATEGORIAL')


# 3. На предыдущем шаге мы исключили из выборки признаки rM_hero и dM_hero, которые показывают, какие именно герои
# играли за каждую команду. Это важные признаки — герои имеют разные характеристики, и некоторые из них
# выигрывают чаще, чем другие. Выясните из данных, сколько различных идентификаторов героев существует в данной игре
def get_heroes(df):
    result = []
    result.extend(df['r1_hero'].unique())
    result.extend(df['r2_hero'].unique())
    result.extend(df['r3_hero'].unique())
    result.extend(df['r4_hero'].unique())
    result.extend(df['r5_hero'].unique())
    result.extend(df['d1_hero'].unique())
    result.extend(df['d2_hero'].unique())
    result.extend(df['d3_hero'].unique())
    result.extend(df['d4_hero'].unique())
    result.extend(df['d5_hero'].unique())
    result = list(set(result))
    result.sort()
    print "Heroes count: %s" % len(result)
    # print "Heroes identifiers:"
    # print result
    return result

heroes = get_heroes(train_df)

# 4. Воспользуемся подходом "мешок слов" для кодирования информации о героях. Пусть всего в игре имеет N различных
# героев. Сформируем N признаков, при этом i-й будет равен нулю, если i-й герой не участвовал в матче; единице,
# если i-й герой играл за команду Radiant; минус единице, если i-й герой играл за команду Dire. Ниже вы можете
# найти код, который выполняет данной преобразование. Добавьте полученные признаки к числовым, которые вы
# использовали во втором пункте данного этапа.
def has_r_hero(df, hero_id):
    """Возвращает столбец bool-значений датафрейма, описывающих принадлежность команде radiant"""

    return (df['r1_hero'] == hero_id) \
        | (df['r2_hero'] == hero_id) \
        | (df['r3_hero'] == hero_id) \
        | (df['r4_hero'] == hero_id) \
        | (df['r5_hero'] == hero_id)


def has_d_hero(df, hero_id):
    """Возвращает столбец bool-значений датафрейма, описывающих принадлежность команде dire"""

    return (df['d1_hero'] == hero_id) \
        | (df['d2_hero'] == hero_id) \
        | (df['d3_hero'] == hero_id) \
        | (df['d4_hero'] == hero_id) \
        | (df['d5_hero'] == hero_id)


def add_heroes_columns(df_dest, df_source, heroes_all):
    columns_count = df_dest.shape[1]
    for hero in heroes_all:
        # one hero cannot be in both teams
        df_dest['hero_' + str(hero)] = has_r_hero(df_source, hero).apply(lambda x: 1 if x else 0) + \
                                       has_d_hero(df_source, hero).apply(lambda x: -1 if x else 0)
    print "Added new %s columns with hero heroes information" % (df_dest.shape[1] - columns_count)
    print

add_heroes_columns(train_df_log, train_df, heroes)

# 5. Проведите кросс-валидацию для логистической регрессии на новой выборке с подбором лучшего параметра регуляризации.
exec_logistic_regression(subtitle='WITH HEROES INFORMATION')


# 6. Постройте предсказания вероятностей победы команды Radiant для тестовой выборки с помощью лучшей из
# изученных моделей (лучшей с точки зрения AUC-ROC на кросс-валидации). Убедитесь, что предсказанные вероятности
# адекватные — находятся на отрезке [0, 1], не совпадают между собой (т.е. что модель не получилась константной).
def run_best():
    print '*' * 80
    print ' ' * 20, 'RUN BEST SOLUTION'
    print '*' * 80

    # train classifier again,this time with optimal hyper-parameter
    X_log = train_df_log.as_matrix()
    scaler = StandardScaler()
    X = scaler.fit_transform(X=X_log)
    cf = LogisticRegression(penalty='l2', C=0.005)
    cf.fit(X, y)

    # predict probabilities for test data
    test_df = pd.read_csv(working_path + "features_test.csv", index_col='match_id')
    del test_df['start_time']
    test_df = test_df.fillna(0)
    add_heroes_columns(test_df, test_df, get_heroes(test_df))
    remove_categorial_features(test_df)

    X_test = test_df.as_matrix()
    X_test = scaler.transform(X_test)
    yprob_pred = cf.predict_proba(X_test)[:, 1]
    print "Predicted prob MIN:", yprob_pred.min()
    print "Predicted prob MAX:", yprob_pred.max()

run_best()
