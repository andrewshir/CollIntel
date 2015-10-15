__author__ = 'Andrew'
import csv
import matplotlib.pyplot as plt
import time
import math
import scipy.stats as stats
import sys

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def define_data_distribution(data):
    chunks_number = 6
    data.sort()
    chunk_size = int(math.ceil(len(data) / float(chunks_number)))
    # get categorized data
    catdata = list(chunks(data, chunk_size))

time_format = "%Y-%m-%d"
remove_data_before_year = 2010

file = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Simulation\\FakePatients.csv"
print "Take data from %s" % file
print "Load workdays and holidays freqs"
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

print "Workdays loaded:", len(workdays)
print "Holidays loaded:", len(holidays)
print

print "Start workdays processing"
dic = workdays
filter = lambda dt: dt.tm_mon in [9,10,11]
# aggregate by years
freq = {}
for daykey in dic.keys():
    datetime = time.strptime(daykey, time_format)

    if not filter(datetime):
        continue

    year = datetime.tm_year
    day = datetime.tm_yday

    # cut data before remove_data_before_year
    if year <= remove_data_before_year:
        continue

    freq.setdefault(day, {})
    freq[day][year] = dic[daykey]

visit_counts = []
# aggregate freqs
for day, dic_year in freq.items():
    v = round(sum([x for x in dic_year.values()])/float(len(dic_year)))
    visit_counts.append(v)
    #print day, v, dic_year.values()

plt.hist(visit_counts, 7)
plt.ylabel("# visits")
plt.show()

zpoints = [216, 238]

obs_freq = []
obs_freq.append(len([x for x in visit_counts if x <=216]))
obs_freq.append(len([x for x in visit_counts if x > 216 and x <= 238]))
obs_freq.append(len([x for x in visit_counts if x > 238]))
print "observations freq", obs_freq

nobs, (min, max), mean, variance, s, k = stats.describe(visit_counts)
#variance = 350
std = math.sqrt(variance)
print "Nobs", nobs
print "Mean", mean
print "Variance", variance

exp_prob = []
exp_prob.append(stats.norm.cdf(216, mean, std))
exp_prob.append(stats.norm.cdf(238, mean, std) - stats.norm.cdf(216, mean, std))
exp_prob.append(1 - stats.norm.cdf(238, mean, std))
print "expected prob", exp_prob

exp_freq = [round(x * nobs) for x in exp_prob]
print "expected freq", exp_freq

chisq, p = stats.chisquare(obs_freq, exp_freq)
print "p", p
print "chisq", chisq

# compare real and artificial data
real_data = []
for daykey in dic.keys():
    datetime = time.strptime(daykey, time_format)

    if filter(datetime):
        real_data.append(dic[daykey])
real_data.sort()

rand_data = stats.norm.rvs(mean, std, len(real_data))
rand_data.sort()

x_values = xrange(len(real_data))
plt.plot(x_values, real_data, 'ro', x_values, rand_data, 'bs')
plt.show()





