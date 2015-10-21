__author__ = 'Andrew'
import FakePatients as fp
import numpy as np
import scipy.stats as stats

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
        print key

    print "Drg values"
    for key in sorted(dic_drg.keys()):
        print key


def split_age(age):
    if age <= 35:
        return 2
    elif 35 < age <= 50:
        return 3
    elif 50 < age <=70:
        return 4
    else:
        return 5

def test_sex():
    contingency_table = {}
    for tup in all_data:
        sline = tup[14]
        sex = tup[10]

        if sline is None:
            continue

        contingency_table.setdefault(sline, {'2': 0, '3': 0})
        contingency_table[sline][sex] += 1

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


def test_age():
    contingency_table = {}
    for tup in all_data:
        sline = tup[14]
        age = split_age(int(tup[9]))

        if sline is None:
            continue

        contingency_table.setdefault(sline, {2: 0, 3: 0, 4: 0, 5: 0})
        contingency_table[sline][age] += 1

    table = []
    for key, dic in contingency_table.items():
        row = []
        for key1 in sorted(dic.keys()):
            row.append(dic[key1])

        nobs, (min, max), mean, variance, s, k = stats.describe(row)
        if min > 5:
            table.append(row)

    chi2, p, dof, ex = stats.chi2_contingency(np.array(table))
    print "chi2", chi2
    print "p", p
    print "dof", dof
    # print ex

def test_test():
    table = [[60, 90, 120], [1, 2, 3]]
    chi2, p, dof, ex = stats.chi2_contingency(np.array(table))
    print "chi2", chi2
    print "p", p
    print "dof", dof

test_test()

test_age()