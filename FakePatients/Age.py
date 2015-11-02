__author__ = 'Andrew'
import FakePatients as fp
import time
import matplotlib.pyplot as plt
import scipy.stats as stats
import math
from FakePatients import split_age

all_data = fp.load_data_with_sline()


def filter_age_data(data, sline):
    result = []
    for tup in data:
        agef_in_years = int(tup[9])
        admit_datef = tup[2]
        slinef = tup[14]

        if slinef is None:
            continue
        if len(admit_datef) == 0:
            continue

        if sline == slinef:
            result.append(agef_in_years)
    return result

def analyze_plot(sline_code, data):
    print "Analysis ages for sline %s" % sline_code
    nobs, (min, max), mean, variance, s, k = stats.describe(data)
    std = math.sqrt(variance)
    print "Nobs", nobs
    print "Mean", mean
    print "Variance", variance
    print "StD", std

    plt.title("Analysis ages for sline %s" % sline_code)
    plt.hist(data)
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
    plt.ylabel("age")
    plt.plot(obs_data, 'b-')
    plt.plot(rand_data, 'ro')
    plt.show()


sline_code = '050'
data = filter_age_data(all_data, sline_code)
# print data
# analyze_plot(sline_code, data)
test([40, 60, 80], data,
     lambda x: stats.norm.cdf(x, loc=70.0, scale=16),
     lambda count: [ x for x in stats.norm.rvs(loc=70.0, scale=16, size=count) if 18 <= x <= 100])


