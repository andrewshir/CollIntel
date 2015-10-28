__author__ = 'Andrew'
import FakePatients as fp
import matplotlib.pyplot as plt
import numpy as np
import math
import scipy.stats as stats

all_data = fp.load_data_with_sline()

def get_data((sex, age, sline)):
    result = []
    for row in all_data:
        admit_date = row[2]
        agef = fp.split_age(int(row[9]))
        sexf = int(row[10])
        slinef = row[14]
        soif = row[8]
        rlos = row[5]

        if slinef is None:
            continue
        if len(admit_date) == 0:
            continue
        if len(rlos) == 0:
            continue
        if len(soif) == 0:
            continue

        if (sex, age, sline) != (sexf, agef, slinef):
            continue

        if int(soif) > 2:
            continue
        datetime = fp.parse_datetime(admit_date)

        result.append(int(rlos))
    return result

def analyze_plot(data):
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

    plt.ylabel("freq")
    plt.xlabel("rlos")
    print freq
    plt.plot(freq.keys(),freq.values())
    plt.show()

def test(zpoints, data, cdf, rvs, ddof = 0):
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
    plt.ylabel("rlos")
    plt.plot(x_values, obs_data, 'ro', x_values, rand_data, '-')
    plt.show()

# sex, age, sline = 2, 3, '050'
sex, age, sline = 3, 4, '387'

data = get_data((sex, age, sline))
# analyze_plot(data)

# 3, 4, '387'
test([1,2,3,4,5], data, lambda x: stats.expon.cdf(x, scale=2.4),
     lambda count: [int(math.floor(x)) for x in stats.expon.rvs(scale=2.4, size=count)])

# 2, 3, '050'
# test([1,2,3,4,5], data, lambda x: stats.expon.cdf(x, scale=2.0),
#      lambda count: [int(math.floor(x)) for x in stats.expon.rvs(scale=2.0, size=count)])

# test([1,2,3,4,5], data, lambda x: stats.poisson.cdf(x, mu=2.0),
#      lambda count: stats.poisson.rvs(mu=2.0, size=count) )
# rlos_list = np.array(rlos_list)
# plt.title("Real LOS")
# plt.hist(rlos_list, bins=25)
# plt.show()

