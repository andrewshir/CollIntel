__author__ = 'Andrew'
import FakePatients as fp
import matplotlib.pyplot as plt
import math
import scipy.stats as stats

print "Winter"
low_filter = 200
zpoints = [220, 240, 260]

workdays, holidays = fp.load_data()
print "Workdays loaded:", len(workdays)
print "Holidays loaded:", len(holidays)
print

s1, s2, s3, s4 = fp.get_season_data(workdays)

#fp.plot_seasons_data(s1, s2, s3, s4)
alldata = s1
data = [x for x in alldata if x > low_filter]
obs_freq = fp.calculate_data_freq(zpoints, data)

print "Observations freq", obs_freq
nobs, (min, max), mean, variance, s, k = stats.describe(data)
std = math.sqrt(variance)
print "Nobs", nobs
print "Mean", mean
print "Variance", variance
print

exp_prob = fp.calculate_exp_prob(zpoints, lambda x: stats.norm.cdf(x, mean, std))
print "Expected prob", exp_prob
exp_freq = fp.convert_prob_2_freq(exp_prob, nobs)
print "Expected freq", exp_freq
print

print "Run Pearson test"
chisq, p = stats.chisquare(obs_freq, exp_freq, 1)
print "p", p
print "chisq", chisq

chi2val = stats.chi2.ppf(0.95, len(obs_freq) - 2)
print "chi2 border value", chi2val
print "H0 is accepted" if chisq < chi2val else "H0 is rejected "

# compare real and predicted data
obs_data = alldata
obs_data.sort()
rand_data = stats.norm.rvs(mean, std, len(obs_data))
rand_data.sort()

x_values = xrange(len(obs_data))
plt.ylabel("# visits per day")
plt.plot(x_values, obs_data, 'ro', x_values, rand_data, 'bs')
plt.show()
