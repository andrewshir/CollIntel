__author__ = 'Andrew'
import FakePatients as fp
import matplotlib.pyplot as plt
from sklearn.neighbors.kde import KernelDensity
import numpy as np
import random
import csv
from datetime import timedelta

training_threshold = 10
alert_count = 50
raw_data, missed_drg = fp.load_data_with_sline()
data = fp.change_to_dict(fp.filter_incomplete_data(raw_data))
print "Rows with following DRG were skipped:",
print missed_drg
print "Filter out %d of %d" % (len(raw_data) - len(data), len(raw_data))

def history(all_data, (sex, age, sline), days=30):
    """Return historical data for selected combination of (sex, age, sline)"""
    start_date = None
    end_date = None
    hist_data = {}
    for row in all_data:
        admit_date = row[2]
        agef_in_years = int(row[9])
        agef = fp.split_age(agef_in_years)
        sexf = int(row[10])
        slinef = row[14]
        rlos = row[5]

        if slinef is None:
            continue
        if len(admit_date) == 0:
            continue

        if len(rlos) == 0:
            continue

        if (sex, age, sline) != (sexf, agef, slinef):
            continue
        datetime = fp.parse_datetime(admit_date)

        start_date = datetime if start_date is None or datetime < start_date else start_date
        end_date = datetime if end_date is None or datetime > end_date else end_date
        hist_data.setdefault(datetime, [])
        hist_data[datetime].append((admit_date, sex, agef_in_years, sline, int(rlos)))

    start_day = random.randint(0, (end_date - start_date).days)
    end_day = start_day + days
    result = []
    for day in range(start_day, end_day + 1):
        day_dt = start_date + timedelta(day)
        if day_dt in hist_data:
            result.extend(hist_data[day_dt])

    return result, start_date + timedelta(start_day), start_date + timedelta(end_day)


def recall_if_empty(lmbd):
    """Calls lambda several times if result is empty"""
    result = lmbd()
    call_count = 1
    while len(result) == 0:
        if call_count >= 10:
            raise RuntimeError("Cannot get non-empty values from lambda")
        result = lmbd()
        call_count += 1
    return result

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
    bad_sl = set()
    for row in data:
        sline = row['sline']
        age = int(row["age"])

        if age <= 0:
            bad_sl.add(sline)
            continue

        sline_ages.setdefault(sline, [])
        sline_ages[sline].append(age)

    for sl in bad_sl:
        print "SL=%s has age values equal or less than zero. Values were ignored" % sl


    for sline, ages in sline_ages.items():
        if len(ages) < alert_count:
            print "SL=%s has less(%d) than %d samples and will be excluded" % (sline, len(ages), alert_count)
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


def train_admit_count(data, show_chart=False):
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
        if len(train_data) < training_threshold:
            print "Too small training set (<%d) for sex %d, age %d, SL %s. Data will be skipped. " % \
                  (training_threshold, sex, age, sline)
            continue

        X = np.array([train_data]).transpose()
        kde = KernelDensity(kernel='tophat', bandwidth=0.5).fit(X)
        kdef = lambda size: [int(round(l[0])) for l in kde.sample(size).tolist()]
        result[tuple] = kde

        if show_chart:
            # print "Sex=%d, Age=%d, SL=%s" % (sex, age, sline)
            # print_freq(ages)
            samples = kdef(len(train_data)) if len(train_data) < 500 else kdef(500)
            # print_freq(samples)

            # hist for train data
            plt.subplot(211)
            plt.title("Admit count train data for Sex=%d, Age=%d, SL=%s" % (sex, age, sline))
            plt.ylabel('freq')
            plt.xlabel('admittance count')
            plt.hist(train_data)

            # estimated density
            plt.subplot(212)
            plt.title("Estimated density Sex=%d, Age=%d, SL=%s" % (sex, age, sline))
            plt.ylabel('freq')
            plt.xlabel('admittance count')
            plt.hist(samples)

            plt.show()

    return result


def train_rlos(data, show_chart=False):
    """Train LOS estimator"""
    """Train patient LOS for triplet (sex, age, sline)"""
    freq = {}
    for row in data:
        sex = int(row["sex"])
        age = fp.split_age(int(row["age"]))
        sline = row["sline"]
        rlos = int(row["rlos"])

        if rlos == 0:
            print "RLOS equals zero for sex %d, age %d, SL %s" % (sex, age, sline)

        tuple = (sex, age, sline)
        freq.setdefault(tuple, [])
        freq[tuple].append(rlos)

    result = {}
    for tuple, train_data in freq.items():
        (sex, age, sline) = tuple
        if len(train_data) < training_threshold:
            print "Too small training set (<%d) for sex %d, age %d, SL %s. Data will be skipped. " % \
                  (training_threshold, sex, age, sline)
            continue

        X = np.array([train_data]).transpose()
        kde = KernelDensity(kernel='tophat', bandwidth=0.5).fit(X)
        kdef = lambda size: [round(l[0]) for l in kde.sample(size).tolist()]
        result[tuple] = kde

        if show_chart:
            # print "Sex=%d, Age=%d, SL=%s" % (sex, age, sline)
            # print_freq(ages)
            samples = kdef(len(train_data)) if len(train_data) < 500 else kdef(500)
            # print_freq(samples)

            # hist for train data
            plt.subplot(211)
            plt.title("RLOS train data for Sex=%d, Age=%d, SL=%s" % (sex, age, sline))
            plt.ylabel('freq')
            plt.xlabel('RLOS')
            plt.hist(train_data)

            # estimated density
            plt.subplot(212)
            plt.title("Estimated density Sex=%d, Age=%d, SL=%s" % (sex, age, sline))
            plt.ylabel('freq')
            plt.xlabel('RLOS')
            plt.hist(samples)

            plt.show()

    return result

# def predict_patient_flow((sex, age, sline), days=30):

def historic_data((sex, age, sline), days=30):
    """Returns historic data for combination (sex, age, sline) and necessary days count"""
    historical_data, sd, ed = history(raw_data, (sex, age, sline), days=30)

    id = "H[%4d-%02d-%02d:%4d-%02d-%02d]" % (sd.year, sd.month, sd.day, ed.year, ed.month, ed.day)
    result = []
    for t in historical_data:
        result.append((id, t[0], t[1], t[2], t[3], t[4]))
    return result

def predict_patient_flow(ages_estimator, admit_count_estimator, rlos_estimator, day_patients_prob,
                         model_count=1, history_count=1, sline_list=None, days=30):
    if sline_list is None:
        sline_list = []
        for common_sline in ages_estimator.keys():
            found = False
            for sex, age, sline in admit_count_estimator.keys():
                if sline == common_sline:
                    found = True
                    break
            if not found:
                continue
            found = False
            for sex, age, sline in rlos_estimator.keys():
                if sline == common_sline:
                    found = True
                    break
            if not found:
                continue
            found = False
            for sex, age, sline in day_patients_prob.keys():
                if sline == common_sline:
                    found = True
                    break
            if not found:
                continue
            sline_list.append(sline)

    # dataset indexes to make dataset identifiers
    model_index = 1
    history_index = 1

    result = []
    for sline in sline_list:
        for sex in [2, 3]:
            for age in [2, 3, 4, 5]:
                tuple = (sex, age, sline)

                if tuple not in admit_count_estimator \
                        or tuple not in rlos_estimator \
                        or tuple not in day_patients_prob:
                    print "Cannot find all estimations for sex %d, age %d, SL %s" % tuple
                    continue

                # add historic data
                for it in xrange(history_count):
                    result.extend(historic_data(tuple, days))
                    history_index += 1

                # model patient flow
                for it in xrange(model_count):
                    rlos_flow_func = lambda: [int(round(l[0]))
                                              for l in rlos_estimator[tuple].sample(100).tolist()]
                    rlos_flow = rlos_flow_func()
                    age_flow_func = lambda: [a for a in ages_estimator[sline](500) if fp.split_age(a) == age]
                    age_flow = recall_if_empty(age_flow_func)
                    admit_count_func = lambda: [int(round(l[0]))
                                                for l in admit_count_estimator[tuple].sample(100).tolist()]
                    admit_flow = admit_count_func()

                    for iday in xrange(days):
                        if day_patients_prob[tuple] == 1.0 or random.random() <= day_patients_prob[tuple]:
                            pat_count = admit_flow.pop()
                            if len(admit_flow) == 0:
                                admit_flow = admit_count_func()
                            for p in xrange(pat_count):
                                id = "M%02d (%d, %d, %s)" % (model_index, sex, age, sline)
                                result.append(
                                    (id, str(iday+1), sex, age_flow.pop(), sline, rlos_flow.pop()))
                                if len(rlos_flow) == 0:
                                    rlos_flow = rlos_flow_func()
                                if len(age_flow) == 0:
                                    age_flow = age_flow_func()

                    model_index += 1
    return result

def save_csv(generated_data, filename='demo.csv'):
    file = fp.working_path + filename
    print "Save results to %s" % file
    with open(file, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['DATASET', 'DATE', 'SEX', 'AGE', 'SL', 'LOS'])

        for row in generated_data:
            writer.writerow(row)


def show_patient_chart2(model, history):
    """Build freq chart for model and historical data"""
    freq_model = {}
    freq_hist = {}
    for x in model:
        freq_model.setdefault(x, 0)
        freq_model[x] += 1

    for x in history:
        freq_hist.setdefault(x, 0)
        freq_hist[x] += 1

    keys = list(set(freq_model.keys() + freq_hist.keys()))
    keys.sort()

    model = []
    history = []
    for key in keys:
        model.append(0 if key not in freq_model else freq_model[key])
        history.append(0 if key not in freq_hist else freq_hist[key])

    N = len(keys)
    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, model, width, color='r')
    rects2 = ax.bar(ind + width, history, width, color='y')

    ax.legend((rects1[0], rects2[0]), ("Model", "History"))
    plt.show()


def build_charts(generated_data):
    rlos_model = []
    rlos_hist = []
    for row in generated_data:
        id = row[0]
        rlos = row[5]
        if id[0] == 'M':
            rlos_model.append(rlos)
        else:
            rlos_hist.append(rlos)

    show_patient_chart2(model=rlos_model, history=rlos_hist)


# ages_estimator = train_age(data, True)
# probs = calc_day_patients_prob()
# # print probs[(2, 3, '050')]
# admit_count_estimator = train_admit_count(data, True)
# rlos_estimator = train_rlos(data, True)

ages_estimator = train_age(data)
probs = calc_day_patients_prob()
admit_count_estimator = train_admit_count(data)
rlos_estimator = train_rlos(data)
output = predict_patient_flow(
    ages_estimator,
    admit_count_estimator,
    rlos_estimator,
    probs,
    sline_list=['050'],
    model_count=5,
    history_count=5,
    days=30)

# save_csv(output, filename='demo3_3.csv')
build_charts(output)