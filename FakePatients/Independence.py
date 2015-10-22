__author__ = 'Andrew'
import FakePatients as fp
import numpy as np
import time
import scipy.stats as stats
from FakePatients import split_age
from FakePatients import show_empty_combinations

all_data = fp.load_data_with_sline()


def show_values():
    """Prints different values for columns in raw data"""
    dic_drg = {}
    dic_age = {}
    dic_sex = {}
    dic_sline = {}
    for tup in all_data:
        drg = tup[7]
        age = tup[9]
        sex = tup[10]
        sline = tup[14]

        dic_drg[drg] = 1
        dic_age[age] = 1
        dic_sex[sex] = 1
        dic_sline[sline] = 1

    print "Age values"
    for key in sorted(dic_age.keys()):
        print key

    print "Sex values"
    for key in sorted(dic_sex.keys()):
        print key

    print "Service line values"
    for key in sorted(dic_sline.keys()):
        if key is None or len(key) == 0:
            continue
        print "'" + key + "',",
    print

    print "Drg values"
    for key in sorted(dic_drg.keys()):
        if key is None or len(key) == 0:
            continue
        print"'" + key + "',",
    print


def show_contingency_table(contingency_table):
    table = []
    for key, dic in contingency_table.items():
        row = []
        for key1 in sorted(dic.keys()):
            row.append(dic[key1])
        table.append(row)

    chi2, p, dof, ex = stats.chi2_contingency(np.array(table))
    print "chi2", chi2
    print "p", p
    print "dof", dof
    # print ex


def get_month(admit_date):
    datetime = time.strptime(admit_date, "%Y-%m-%d")
    return datetime.tm_mon


def test_sex():
    contingency_table = {}
    for tup in all_data:
        sline = tup[14]
        sex = int(tup[10])

        if sline is None:
            continue

        contingency_table.setdefault(sline, {2: 0, 3: 0})
        contingency_table[sline][sex] += 1

    show_contingency_table(contingency_table)


def test_age():
    contingency_table = {}
    for tup in all_data:
        sline = tup[14]
        age = split_age(int(tup[9]))

        if sline is None:
            continue

        contingency_table.setdefault(sline, {2: 0, 3: 0, 4: 0, 5: 0})
        contingency_table[sline][age] += 1

    show_contingency_table(contingency_table)


def test_age_sex():
    contingency_table = {}
    for tup in all_data:
        age = split_age(int(tup[9]))
        sex = int(tup[10])

        contingency_table.setdefault(age, {2: 0, 3: 0})
        contingency_table[age][sex] += 1

    show_contingency_table(contingency_table)


def test_sline_month():
    contingency_table = {}
    sline_list = ['040', '045', '050', '055', '065', '070', '085', '090', '095', '125', '129', '132', '133', '135', '137', '145', '165', '170', '245', '250', '252', '255', '262', '267', '271', '272', '274', '276', '280', '283', '293', '294', '296', '325', '330', '370', '385', '387', '390']
    for tup in all_data:
        admit_date = tup[2]
        sline = tup[14]

        if sline is None:
            continue
        if len(admit_date) == 0:
            continue

        month = get_month(admit_date)

        empty_dict = {}
        for v in sline_list:
            empty_dict[v] = 0

        contingency_table.setdefault(month, empty_dict)
        contingency_table[month][sline] += 1

    show_contingency_table(contingency_table)


def test_age_month():
    contingency_table = {}
    for tup in all_data:
        admit_date = tup[2]
        age = split_age(int(tup[9]))

        if len(admit_date) == 0:
            continue

        month = get_month(admit_date)

        contingency_table.setdefault(month, {2: 0, 3: 0, 4: 0, 5: 0})
        contingency_table[month][age] += 1

    show_contingency_table(contingency_table)


def test_sex_month():
    contingency_table = {}
    for tup in all_data:
        admit_date = tup[2]
        sex = int(tup[10])

        if len(admit_date) == 0:
            continue

        month = get_month(admit_date)

        contingency_table.setdefault(month, {2: 0, 3: 0})
        contingency_table[month][sex] += 1

    show_contingency_table(contingency_table)


def test_test():
    table = [[62, 88, 117], [1, 2, 3]]
    chi2, p, dof, ex = stats.chi2_contingency(np.array(table))
    print "chi2", chi2
    print "p", p
    print "dof", dof

# show_values()
# show_empty_combinations()
show_empty_combinations()

"""
Results so far:

Strongly dependent:
age - sline
sex - sline

Weakly dependent:
age - month
age - sex
sline - month

Independent:
sex - month

"""