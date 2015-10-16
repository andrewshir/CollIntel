__author__ = 'Andrew'

import math
import scipy.stats as stats
import numpy as np

observed_values = [1, 3, 5, 7, 9, 11]
observed_freqs = [3, 16, 28, 32, 14, 7]
obs = []
for i in range(len(observed_freqs)):
    for j in range(observed_freqs[i]):
        obs.append(observed_values[i])

obs = np.array(obs)
observed_values = np.array(observed_values)
observed_freqs = np.array(observed_freqs)

nobs, (min, max), mean, variance, s, k = stats.describe(obs)
std = math.sqrt(variance)
print "Mean", mean
print "Variance", variance
print "Standard deviation", std

expected_prob = [ stats.norm.cdf(observed_values[i]+1, mean, std) - stats.norm.cdf(observed_values[i]-1, mean, std)
                  for i in range(len(observed_values))]
expected_prob = np.array(expected_prob)
expected_freqs = np.array([int(round(x * nobs)) for x in expected_prob])

#expected_freqs = [ x * nobs for x in expected_prob ]
#expected_freqs = np.array(expected_freqs)

#print expected_prob
print "Expected", expected_freqs
print "Observed", observed_freqs

print "Run Pearson test:"
chisq, p = stats.chisquare(observed_freqs, expected_freqs, 1)
print "p", p
print "chisq statistics", chisq

chi2val = stats.chi2.ppf(0.95, len(observed_values) - 2)
print "chi2 border value", chi2val
print "H0 is accepted" if chisq < chi2val else "H0 is rejected "