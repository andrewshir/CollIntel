# -*- coding: utf-8 -*-
import sys
reload(sys)
import pandas as pd
from sklearn.cross_validation import KFold
from sklearn.cross_validation import cross_val_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import time
import datetime
import numpy as np


sys.setdefaultencoding('utf-8')
working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week7\\"

# 1. Считайте таблицу с признаками из файла features.csv с помощью кода, приведенного выше.
# Удалите признаки, связанные с итогами матча (они помечены в описании данных как отсутствующие в тестовой выборке).

train_df = pd.read_csv(working_path + "features.csv", index_col='match_id')
del train_df['duration']
del train_df['tower_status_radiant']
del train_df['tower_status_dire']
del train_df['barracks_status_radiant']
del train_df['barracks_status_dire']

# 2. Проверьте выборку на наличие пропусков с помощью функции count(), которая для каждого столбца показывает
# число заполненных значений. Много ли пропусков в данных?
# Запишите названия признаков, имеющих пропуски, и попробуйте для любых двух из них дать обоснование,
# почему их значения могут быть пропущены.
row_count = train_df.shape[0]
counts = train_df.count()
print "Columns with missed values:"
print counts[counts < row_count]
print

# 3. Замените пропуски на нули с помощью функции fillna().
train_df = train_df.fillna(0)

# 4. Какой столбец содержит целевую переменную? Запишите его название.
y = train_df['radiant_win'].as_matrix()
del train_df['radiant_win']
X = train_df.as_matrix()

# 5. Забудем, что в выборке есть категориальные признаки, и попробуем обучить градиентный бустинг над деревьями на
# имеющейся матрице "объекты-признаки".
kfold = KFold(n=row_count, n_folds=5, shuffle=True, random_state=123)


# Оцените качество градиентного бустинга (GradientBoostingClassifier) с помощью данной кросс-валидации,
# попробуйте при этом разное количество деревьев
def exec_gradient_boosting():
    print '*' * 80
    print ' ' * 20, 'APPROACH A: GRADIENT BOOSTING'
    print '*' * 80

    for num_estimators in xrange(5, 50, 5):
        print "Trees number: %d" % num_estimators

        cf = GradientBoostingClassifier(n_estimators=num_estimators)

        start_time = datetime.datetime.now()
        scores = cross_val_score(estimator=cf, cv=kfold, scoring='roc_auc', X=X, y=y)
        time_elapsed = datetime.datetime.now() - start_time

        print "Min score: %5f, Max score: %5f, Mean score: %5f" % (scores.min(), scores.max(), scores.mean())
        print "Time elapsed: %s" % time_elapsed
        print

#exec_gradient_boosting()


# 1. Оцените качество логистической регрессии (sklearn.linear_model.LogisticRegression с L2-регуляризацией)
# с помощью кросс-валидации по той же схеме, которая использовалась для градиентного бустинга. Подберите при этом
# лучший параметр регуляризации (C).
train_df_log = train_df.copy()

def exec_logistic_regression():
    print '*' * 80
    print ' ' * 20, 'APPROACH B: LOGISTIC REGRESSION'
    print '*' * 80

    X_log = train_df_log.as_matrix()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X=X_log)

    for C in [0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]:
        print "C=%f" % C
        cf = LogisticRegression(penalty='l2', C=C)
        start_time = datetime.datetime.now()
        scores = cross_val_score(estimator=cf, cv=kfold, scoring='roc_auc', X=X_scaled, y=y)
        time_elapsed = datetime.datetime.now() - start_time

        print "Min score: %5f, Max score: %5f, Mean score: %5f" % (scores.min(), scores.max(), scores.mean())
        print "Time elapsed: %s" % time_elapsed
        print

#exec_logistic_regression()

# 2. Среди признаков в выборке есть категориальные, которые мы использовали как числовые,
#  что вряд ли является хорошей идеей. Категориальных признаков в этой задаче одиннадцать:
# lobby_type и r1_hero, r2_hero, ..., r5_hero, d1_hero, d2_hero, ..., d5_hero.
# Уберите их из выборки, и проведите кросс-валидацию для логистической регрессии на новой выборке с подбором
# лучшего параметра регуляризации.
del train_df_log['lobby_type']
del train_df_log['r1_hero']
del train_df_log['r2_hero']
del train_df_log['r3_hero']
del train_df_log['r4_hero']
del train_df_log['r5_hero']
del train_df_log['d1_hero']
del train_df_log['d2_hero']
del train_df_log['d3_hero']
del train_df_log['d4_hero']
del train_df_log['d5_hero']

# exec_logistic_regression()

# 3. На предыдущем шаге мы исключили из выборки признаки rM_hero и dM_hero, которые показывают, какие именно герои
# играли за каждую команду. Это важные признаки — герои имеют разные характеристики, и некоторые из них
# выигрывают чаще, чем другие. Выясните из данных, сколько различных идентификаторов героев существует в данной игре
heroes = []
heroes.extend(train_df['r1_hero'].unique())
heroes.extend(train_df['r2_hero'].unique())
heroes.extend(train_df['r3_hero'].unique())
heroes.extend(train_df['r4_hero'].unique())
heroes.extend(train_df['r5_hero'].unique())
heroes.extend(train_df['d1_hero'].unique())
heroes.extend(train_df['d2_hero'].unique())
heroes.extend(train_df['d3_hero'].unique())
heroes.extend(train_df['d4_hero'].unique())
heroes.extend(train_df['d5_hero'].unique())
heroes = list(set(heroes))
heroes.sort()
print "Heroes identifiers (count=%d):" % len(heroes)
print heroes


# 4. Воспользуемся подходом "мешок слов" для кодирования информации о героях. Пусть всего в игре имеет N различных
# героев. Сформируем N признаков, при этом i-й будет равен нулю, если i-й герой не участвовал в матче; единице,
# если i-й герой играл за команду Radiant; минус единице, если i-й герой играл за команду Dire. Ниже вы можете
# найти код, который выполняет данной преобразование. Добавьте полученные признаки к числовым, которые вы
# использовали во втором пункте данного этапа.
def has_r_hero(df, hero_id):
    return (df['r1_hero'] == hero_id) \
        | (df['r2_hero'] == hero_id) \
        | (df['r3_hero'] == hero_id) \
        | (df['r4_hero'] == hero_id) \
        | (df['r5_hero'] == hero_id)


def has_d_hero(df, hero_id):
    return (df['d1_hero'] == hero_id) \
        | (df['d2_hero'] == hero_id) \
        | (df['d3_hero'] == hero_id) \
        | (df['d4_hero'] == hero_id) \
        | (df['d5_hero'] == hero_id)


print "DF shape before:", train_df_log.shape
for hero in heroes:
    # one hero cannot be in both teams
    train_df_log['hero_' + str(hero)] = has_r_hero(train_df, hero).apply(lambda x: 1 if x else 0) + \
                                        has_d_hero(train_df, hero).apply(lambda x: -1 if x else 0)
print "DF shape after:", train_df_log.shape

# 5. Проведите кросс-валидацию для логистической регрессии на новой выборке с подбором лучшего параметра регуляризации.
exec_logistic_regression()




