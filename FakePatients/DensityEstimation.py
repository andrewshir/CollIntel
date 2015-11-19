__author__ = 'Andrew'
import FakePatients as fp
import matplotlib.pyplot as plt
from sklearn.neighbors.kde import KernelDensity
import numpy as np

raw_data, missed_drg = fp.load_data_with_sline()
data = fp.change_to_dict(fp.filter_incomplete_data(raw_data))
print "Rows with following DRG were skipped:",
print missed_drg
print "Filter out %d of %d" % (len(raw_data) - len(data), len(raw_data))


def train_age(data, show_chart=False):
    """Train age estimator for each SL"""
    def print_freq(data):
        freq = {}
        length = float(len(data))
        for x in data:
            xcat = fp.split_age(x)
            freq.setdefault(xcat, 0)
            freq[xcat] += 1
        for x in sorted(freq.keys()):
            print "%d: %.2f" % (x, round(freq[x]/length, 2)),
        print

    sline_ages = {}
    for row in data:
        sline = row['sline']
        age = int(row["age"])

        if age <= 0:
            print "SL=%s has age equals or less than zero (%d). Value is ignored" % (sline, age)
            continue

        sline_ages.setdefault(sline, [])
        sline_ages[sline].append(age)

    alert_count = 50
    for sline, ages in sline_ages.items():
        if len(ages) < alert_count:
            print "Sline %s has less(%d) than %d samples and will be excluded" % (sline, len(ages), alert_count)
            del sline_ages[sline]

    result = {}
    for sline,ages in sline_ages.items():
        X = np.array([ages]).transpose()
        kde = KernelDensity(kernel='tophat', bandwidth=1.0).fit(X)
        kdef = lambda size: [round(l[0]) for l in kde.sample(size).tolist()]
        result[sline] = kdef

        if show_chart:

            print "SL=%s" % sline
            print_freq(ages)
            samples = kdef(len(ages)) if len(ages) < 500 else kdef(500)
            print_freq(samples)

            # hist for train data
            plt.subplot(211)
            plt.title("Age train data for SL=%s" %(sline))
            plt.ylabel('freq')
            plt.xlabel('age category')
            plt.hist(ages)

            # estimated density
            plt.subplot(212)
            plt.title("Estimated density %s" % sline)
            plt.ylabel('freq')
            plt.xlabel('age category')
            plt.hist(samples)

            plt.show()
    return result

def calc_day_patients_prob():
    return fp.get_patients_freq(raw_data)

def train_admit_number(data, show_chart=False):
    """Train patient admittance number for triplet (sex, age, sline)"""
    freq = {}
    for row in data:
        sex = int(row["sex"])
        age = fp.split_age(int(row["age"]))
        sline = row["sline"]
        admit = row["admit"]

        tuple = (sex, age, sline)
        freq.setdefault(tuple, {})
        freq[tuple].setdefault(admit, 0)
        freq[tuple][admit] += 1

    result = {}
    for tuple, days in freq.items():
        (sex, age, sline) = tuple
        train_data = days.values()
        if len(train_data) < 10:
            print "Too small training set for sex %d, age %d, SL %s. Data will be skipped. " % tuple
            continue

        X = np.array([train_data]).transpose()
        kde = KernelDensity(kernel='tophat', bandwidth=0.5).fit(X)
        kdef = lambda size: [round(l[0]) for l in kde.sample(size).tolist()]
        result[tuple] = kdef

        if show_chart:
            print "SL=%s" % sline
            # print_freq(ages)
            samples = kdef(len(train_data)) if len(train_data) < 500 else kdef(500)
            # print_freq(samples)

            # hist for train data
            plt.subplot(211)
            plt.title("Admit numbers train data for SL=%s" %(sline))
            plt.ylabel('freq')
            plt.xlabel('admittance number')
            plt.hist(train_data)

            # estimated density
            plt.subplot(212)
            plt.title("Estimated density %s" % sline)
            plt.ylabel('freq')
            plt.xlabel('admittance number')
            plt.hist(samples)

            plt.show()

    return result


# ages_estimator = train_age(data, True)
# probs = calc_day_patients_prob()
# print probs[(2, 3, '050')]
admit_number_estimator = train_admit_number(data, True)

