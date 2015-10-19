__author__ = 'Andrew'
import csv
import matplotlib.pyplot as plt
import time

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








