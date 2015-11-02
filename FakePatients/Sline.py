__author__ = 'Andrew'
import FakePatients as fp
import time
import matplotlib.pyplot as plt
import scipy.stats as stats
import math
from FakePatients import split_age

all_data = fp.load_data_with_sline()
# Here are sline which are presented almost every day (at least 360 days in year )
fit_sline = ['276', '070', '090', '390', '274', '135', '129', '250', '050', '255', '280', '283', '145', '065', '085'
             , '245', '262', '267', '125', '387', '165', '132', '296']
YEAR = 2012
FULL_YEARS = [2011, 2012, 2013]

def show_sline_freq(year=YEAR):
    """Prints sline counts for a year"""
    sline_freq = {}
    for tuple in all_data:
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

    print "Sline freq for %s year" % year
    print "Sline total:", len(sline_freq)
    print "Sline count"

    for sline, count in sline_freq.items():
        print sline, count


def sline_year_fitness():
    """Prints number of y-days with patient admittance for a sline"""
    fitness = {}
    for tuple in all_data:
        admit_date = tuple[2]
        sline = tuple[14]
        if sline is None:
            continue

        admit_date = tuple[2]
        if len(admit_date) == 0:
            continue

        datetime = time.strptime(admit_date, "%Y-%m-%d")
        if int(datetime.tm_year)<= fp.remove_data_before_year:
            continue

        # if int(datetime.tm_year) != YEAR:
        #     continue

        fitness.setdefault(sline, {})
        fitness[sline][datetime.tm_yday] = 1

    print "Sline, days in year"
    for sline, ydays in fitness.items():
        print sline, len(ydays), "!!" if len(ydays) < 360 else ""


def get_avg_sline_data(sline_code, all_data):
    """Return sline average year data"""
    freq = {}
    for tuple in all_data:
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

        # if datetime.tm_year not in (2011, 2012, 2013):
        #     continue

        freq.setdefault(datetime.tm_year, {})
        freq[datetime.tm_year].setdefault(datetime.tm_yday, 0)
        freq[datetime.tm_year][datetime.tm_yday] += 1

    # count #visits freqs for different years
    vfreq = {}
    for year, days in freq.items():
        for v in days.values():
            vfreq.setdefault(v, {})
            vfreq[v].setdefault(year, 0)
            vfreq[v][year] += 1

    result_dict = {}
    for v, years in vfreq.items():
        result_dict[v] = int(round(sum(years.values())/float(len(years))))
        # print v, result_dict[v], years.values()

    result = []
    for key, value in result_dict.items():
        result.extend([key for x in xrange(value)])
    return result


def get_latest_sline_data(sline_code, all_data, n=30):
    """Returns latest sline data"""
    data = {}
    for tup in all_data:
        admit_date = tup[2]
        sline = tup[14]

        if sline != sline_code:
            continue
        if len(admit_date) == 0:
            continue
        data.setdefault(admit_date, 0)
        data[admit_date] += 1
    keys = sorted(data.keys())
    if len(keys) > n:
        keys = keys[-n:]

    result=[]
    for key in keys:
        result.append(data[key])
    return result


def hist_sline(sline_code, bins, values=None):
    """Build hist for day freqs for a given sline"""
    if values is None:
        values = get_avg_sline_data(sline_code)

    plt.title("Freq for sline %s" %(sline_code))
    plt.hist(values,bins)
    plt.ylabel('visit freq')
    plt.xlabel('# visits per day')
    plt.show()


def add_zeros(data):
    zero_count = 365 - len(data)
    if zero_count<0: zero_count = 0
    result=[]
    result.extend([0 for x in xrange(zero_count)])
    result.extend(data)
    return result


def filter_data(data, (sexf, agef, slinef)):
    result = []
    for tup in data:
        age = split_age(int(tup[9]))
        sex = int(tup[10])
        admit_date = tup[2]
        sline = tup[14]

        if sline is None:
            continue
        if len(admit_date) == 0:
            continue

        if age == agef and sex == sexf and sline == slinef:
            result.append(tup)
    return result


def analyze_hist(sline_code, data, bins=7):
    print "Analysis sline %s" % sline_code
    nobs, (min, max), mean, variance, s, k = stats.describe(data)
    std = math.sqrt(variance)
    print "Nobs", nobs
    print "Mean", mean
    print "Variance", variance
    print "StD", std

    hist_sline(sline_code, bins, data)

def analyze_plot(sline_code, data):
    print "Analysis sline %s" % sline_code
    nobs, (min, max), mean, variance, s, k = stats.describe(data)
    std = math.sqrt(variance)
    print "Nobs", nobs
    print "Mean", mean
    print "Variance", variance
    print "StD", std

    freq = {}
    for x in data:
        freq.setdefault(x, 0)
        freq[x] += 1

    plt.title("Analysis sline %s" % sline_code)
    plt.ylabel("#visits")
    plt.xlabel("number of patients per day")
    plt.plot(freq.keys(),freq.values())
    plt.show()


def test(zpoints, data, cdf, rvs, ddof = 1):
    obs_freq = fp.calculate_data_freq(zpoints, data)
    exp_prob = fp.calculate_exp_prob(zpoints, cdf)
    exp_freq = fp.convert_prob_2_freq(exp_prob, len(data))
    print "Observations freq", obs_freq
    print "Expected freq", exp_freq
    print "Run Pearson test"
    chisq, p = stats.chisquare(obs_freq, exp_freq, ddof)
    print "p", p
    print "chisq", chisq
    chi2val = stats.chi2.ppf(0.95, len(obs_freq) - 1 - ddof)
    print "chi2 border value", chi2val
    print "H0 is accepted" if chisq < chi2val else "H0 is rejected "

    obs_data = data
    obs_data.sort()
    rand_data = rvs(len(obs_data))
    rand_data = [x if x > 1 else 1 for x in rand_data]
    rand_data.sort()

    x_values = xrange(len(obs_data))
    plt.ylabel("# visits per day")
    plt.plot(x_values, obs_data, 'ro', x_values, rand_data, '-')
    plt.show()


def predict(sline_dstr):
    # sline_dstr.code
    # sline_dstr.rvs(30)

    historical_data = []

#
# sline_dstr = [
#     SlineDstr('070', [2,3,4,5], lambda count: stats.poisson.rvs(mu=2.6, size=count))
#     ,SlineDstr('090', [2,3,4], lambda count: stats.poisson.rvs(mu=2.19, size=count))
#     ,SlineDstr('050', [3,4,5,6], lambda count: stats.poisson.rvs(mu=2.19, size=count))
#     ,SlineDstr('165', [2,3,4,5], lambda count: stats.poisson.rvs(mu=2.0, size=count))
#     ,SlineDstr('250', [2,3,4,5], lambda count: stats.poisson.rvs(mu=2.0, size=count))
#     ,SlineDstr('280', [2,3,4,5], lambda count: stats.poisson.rvs(mu=2.21, size=count))
#     ,SlineDstr('387', [3,4,5,6], lambda count: stats.poisson.rvs(mu=2.9, size=count))
#     ,SlineDstr('145', [2,4], lambda count: stats.poisson.rvs(mu=2.81, size=count))
#     ]

selected = [
    # Cardiology 35-50
    (2, 3, '050')
    # Cardiology 50-70
    ,(2, 4, '050')
    # Cardiology 50-70
    ,(3, 4, '050')
    # Urological Surgery 50-70
    ,(2, 4, '387')
    # Urological Surgery 50-70
    ,(3, 4, '387')
]

# for sline_code in fit_sline:
sline_code = '050'
data = filter_data(all_data, (3, 5, sline_code))
data = get_avg_sline_data(sline_code, data)
# print len(data)
# print data
# analyze_plot(sline_code, data)

# analyze_hist(sline_code, data)
# test([2,3], data, lambda x: stats.poisson.cdf(x, mu=1.44), lambda count: stats.poisson.rvs(mu=1.3, size=count), 0)
# test([2,3,4,5], data, lambda x: stats.poisson.cdf(x, mu=2.6), lambda count: stats.poisson.rvs(mu=2.6, size=count))


test([2,3,4,5], data, lambda x: stats.poisson.cdf(x, mu=2.0), lambda count: stats.poisson.rvs(mu=2.0, size=count))



# show_sline_freq()

# predict(SlineDstr('050', [], lambda count: stats.poisson.rvs(mu=1.17, size=count)))


