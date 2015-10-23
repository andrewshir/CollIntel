__author__ = 'Andrew'
import csv
import matplotlib.pyplot as plt
import time
import datetime

import numpy as np

time_format = "%Y-%m-%d"
remove_data_before_year = 2010
working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\FakePatients\\"


def load_data(data_file = "FakePatients.csv"):
    file = working_path + data_file
    print "Take data from %s" % file
    workdays = {}
    holidays = {}
    with open(file, "rb") as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')

        # skip the header
        reader.next()

        for row in reader:
            admit_date = row[2]
            if len(admit_date) == 0:
                continue

            datetime = time.strptime(admit_date, "%Y-%m-%d")
            if datetime.tm_wday in (5,6):
                holidays.setdefault(admit_date, 0)
                holidays[admit_date] += 1
            else:
                workdays.setdefault(admit_date, 0)
                workdays[admit_date] += 1
    return workdays, holidays


def load_mapping(mapping_file="Mapping.csv"):
    file = working_path + mapping_file
    print "Load mappping from %s" % file

    with open(file, "rb") as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')

        # skip the header
        reader.next()

        result = {}
        for row in reader:
            service_line = row[0]
            drg = row[2]

            if drg in result:
                raise RuntimeError("Duplicate DRG in mapping")
            result[drg] = service_line
        return result

def load_data_with_sline(data_file = "FakePatients.csv"):
    """Loads data as list of tuples, adde sline at the end"""

    mapping = load_mapping()
    file = working_path + data_file
    print "Load DRG data from %s" % file

    data = []

    with open(file, "rb") as f:
        reader = csv.reader(f)

        # skip header
        reader.next()

        for row in reader:
            period = row[0]
            visit = row[1]
            admit = row[2]
            dis = row[3]
            blos = row[4]
            rlos = row[5]
            stay = row[6]
            drg = row[7]
            soi = row[8]
            age = row[9]
            sex = row[10]
            isdied = row[11]
            ddx_total = row[12]
            proc_total = row[13]
            sline = None

            if drg in mapping:
                sline = mapping[drg]

            data.append((period, visit, admit, dis, blos, rlos, stay, drg, soi, age, sex, isdied, ddx_total, proc_total, sline))
    return data

def get_season_data(dic_freq_by_days):
    seasons = [{}, {}, {}, {}]

    for daykey in dic_freq_by_days.keys():
        datetime = time.strptime(daykey, time_format)

        year = datetime.tm_year
        day = datetime.tm_yday

        # cut data before remove_data_before_year
        if year <= remove_data_before_year:
            continue

        quarter_num = 1 if datetime.tm_mon in [3, 4, 5] else \
                      2 if datetime.tm_mon in [6, 7, 8] else \
                      3 if datetime.tm_mon in [9, 10, 11] else \
                      0

        seasons[quarter_num].setdefault(day, {})
        seasons[quarter_num][day][year] = dic_freq_by_days[daykey]

    seasons_data = [[], [], [], []]
    # aggregate freqs
    for i in range(len(seasons_data)):
        for day, dic_year in seasons[i].items():
            v = int(round(np.mean(dic_year.values())))
            seasons_data[i].append(v)

    return seasons_data


def plot_data(data, bins=5):
    plt.hist(data, bins)
    plt.xlabel("# visits")
    plt.show()


def plot_seasons_data(s1, s2, s3, s4):
    plt.hist(s1, 7)
    plt.title("Winter")
    plt.xlabel("# visits")
    plt.show()

    plt.hist(s2, 7)
    plt.title("Spring")
    plt.xlabel("# visits")
    plt.show()

    plt.hist(s3, 7)
    plt.title("Summer")
    plt.xlabel("# visits")
    plt.show()

    plt.hist(s4, 7)
    plt.title("Autumn")
    plt.xlabel("# visits")
    plt.show()


def calculate_data_freq(borders, data):
    result = []
    if len(borders) == 0:
        return result

    result.append(len([x for x in data if x <= borders[0]]))
    for i in range(1, len(borders)):
        result.append(len([x for x in data if borders[i-1] < x <= borders[i]]))
    result.append(len([x for x in data if borders[-1] < x ]))
    return result


def calculate_exp_prob(borders, cdf):
    result = []
    if len(borders) == 0:
        return result

    result.append(cdf(borders[0]))
    for i in range(1, len(borders)):
        result.append(cdf(borders[i]) - cdf(borders[i-1]))
    result.append(1 - cdf(borders[-1]))
    return result


def convert_prob_2_freq(probs, nobs):
    return [int(round(x * nobs)) for x in probs]

def split_age(age):
    if age <= 35:
        return 2
    elif 35 < age <= 50:
        return 3
    elif 50 < age <=70:
        return 4
    else:
        return 5

def get_empty_combinations(all_data=None):
    """Allows estimate data presence for different categories"""
    if all_data is None:
        all_data = load_data_with_sline()

    sex_list, age_list, sline_list = get_value_sets()

    result = []
    data = {}
    for s in sex_list:
        data[s] = {}
        for a in age_list:
            data[s][a] = {}
            for sl in sline_list:
                data[s][a][sl] = 0

    for tup in all_data:
        age = split_age(int(tup[9]))
        sex = int(tup[10])
        admit_date = tup[2]
        sline = tup[14]

        if sline is None:
            continue
        if len(admit_date) == 0:
            continue

        data[sex][age][sline] += 1

    for s in sex_list:
        for a in age_list:
            for sl in sline_list:
                if data[s][a][sl] == 0:
                    result.append((s,a,sl))
                    continue

    return result


def show_empty_combinations(all_data=None):
    list = get_empty_combinations(all_data)
    for (s,a,sl) in list:
        print "Sex %d, age %d, sline %s has no data" % (s, a, sl)
    print "Total:", len(list)

def parse_struct_time(str_date):
    return time.strptime(str_date, time_format)

def parse_datetime(str_date):
    dt = time.strptime(str_date, time_format)
    return datetime.datetime(dt.tm_year, dt.tm_mon, dt.tm_mday, dt.tm_hour, dt.tm_min, dt.tm_sec)


def get_value_sets():
    return [2, 3], [2, 3, 4, 5], ['040', '045', '050', '055', '065', '070', '085', '090', '095', '125', '129', '132', '133', '135', '137', '145', '165', '170', '245', '250', '252', '255', '262', '267', '271', '272', '274', '276', '280', '283', '293', '294', '296', '325', '330', '370', '385', '387', '390']


def get_patients_freq(all_data=None):
    """Returns probabilities of admittance of a patient with some (sex, age, sline)"""
    if all_data is None:
        all_data = load_data_with_sline()

    sex_list, age_list, sline_list = get_value_sets()


    data = {}
    for s in sex_list:
        data[s] = {}
        for a in age_list:
            data[s][a] = {}
            for sl in sline_list:
                data[s][a][sl] = {}

    start_date = None
    end_date = None
    for tup in all_data:
        age = split_age(int(tup[9]))
        sex = int(tup[10])
        admit_date = tup[2]
        sline = tup[14]

        if sline is None:
            continue
        if len(admit_date) == 0:
            continue
        datetime = parse_datetime(admit_date)
        start_date = datetime if start_date is None or datetime < start_date else start_date
        end_date = datetime if end_date is None or datetime > end_date else end_date
        data[sex][age][sline][admit_date] = 1

    days_count = (end_date - start_date).days

    result = {}
    for s in sex_list:
        for a in age_list:
            for sl in sline_list:
                result[(s, a, sl)] = len(data[s][a][sl]) / float(days_count)

    return result





