__author__ = 'Andrew'
import FakePatients
import time
import matplotlib.pyplot as plt

data = FakePatients.load_data_with_sline()
# Here are sline which are presented almost every day (at least 360 days in year )
fit_sline = ['276', '070', '090', '390', '274', '135', '129', '250', '050', '255', '280', '283', '145', '065', '085'
             , '245', '262', '267', '125', '387', '165', '132', '296']
YEAR = 2012


def show_sline_freq(year=YEAR):
    """Prints sline counts for a year"""
    sline_freq = {}
    for tuple in data:
        sline = tuple[14]
        if sline is None:
            continue

        admit_date = tuple[2]
        if len(admit_date) == 0:
            continue

        datetime = time.strptime(admit_date, "%Y-%m-%d")
        if int(datetime.tm_year) != year:
            continue

        sline_freq.setdefault(sline, 0)
        sline_freq[sline] += 1

    print "Sline freq for 2012 year"
    print "Sline total:", len(sline_freq)
    print "Sline count"

    for sline, count in sline_freq.items():
        print sline, count


def sline_year_fitness():
    """Prints number of y-days with patient admittance for a sline"""
    fitness = {}
    for tuple in data:
        admit_date = tuple[2]
        sline = tuple[14]
        if sline is None:
            continue

        admit_date = tuple[2]
        if len(admit_date) == 0:
            continue

        datetime = time.strptime(admit_date, "%Y-%m-%d")
        if int(datetime.tm_year)<= FakePatients.remove_data_before_year:
            continue

        # if int(datetime.tm_year) != YEAR:
        #     continue

        fitness.setdefault(sline, {})
        fitness[sline][datetime.tm_yday] = 1

    print "Sline, days in year"
    for sline, ydays in fitness.items():
        print sline, len(ydays), "!!" if len(ydays) < 360 else ""


def sline(sline_code, bins=7):
    """Plots day freqs for a given sline"""
    freq = {}
    for tuple in data:
        admit_date = tuple[2]
        sline = tuple[14]
        if sline is None:
            continue

        if sline != sline_code:
            continue

        admit_date = tuple[2]
        if len(admit_date) == 0:
            continue

        datetime = time.strptime(admit_date, "%Y-%m-%d")
        # if int(datetime.tm_year) != YEAR:
        #     continue

        if int(datetime.tm_year)<= FakePatients.remove_data_before_year:
            continue

        freq.setdefault(admit_date, {})
        freq[admit_date].setdefault(datetime.tm_year, 0)
        freq[admit_date][datetime.tm_year] += 1

    keys = freq.keys()
    keys.sort()

    values = []

    for daykey in keys:
        #print daykey, freq[daykey]
        value = sum(freq[daykey].values())/len(freq[daykey])
        values.append(value)

    plt.title("Freq for sline %s in %d" %(sline_code, YEAR))
    plt.hist(values,bins)
    plt.ylabel('visit freq')
    plt.xlabel('# visits per day')
    plt.show()


class SlineDstr(object):
    """Describes sline patient count distribution"""

    def __init__(self, code, rvs=None, prob=0.0):
        # sline code
        self.code = code
        # function to get number of patient with this sline per day
        self.rvs = rvs
        # probability of admittance of patient with this sline
        self.prob = prob


sline('276')
# sline_year_fitness()
# show_sline_freq()