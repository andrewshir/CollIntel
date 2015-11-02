__author__ = 'Andrew'
from Repository import Repository
from Repository import DistrInfo
from FakePatients import get_patients_freq
import scipy.stats as stats
import matplotlib.pyplot as plt
import math


repo = Repository()
# Cardiology 35-50
repo.add_patients_count_distr((2, 3, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.17, size=x), 0.14))
repo.add_rlos_distr((2, 3, '050'), lambda count: [int(math.floor(x)) for x in stats.expon.rvs(scale=2.0, size=count)])
# Cardiology 50-70
repo.add_patients_count_distr((2, 4, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.46, size=x), 0.45))
# Cardiology 50-70
repo.add_patients_count_distr((3, 4, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.3, size=x), 0.336))
# Urological Surgery 50-70
repo.add_patients_count_distr((2, 4, '387'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.44, size=x), 0.267))
# Urological Surgery 50-70
repo.add_patients_count_distr((3, 4, '387'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.17, size=x), 0.08))
repo.add_rlos_distr((3, 4, '387'), lambda count: [int(math.floor(x)) for x in stats.expon.rvs(scale=2.4, size=count)])


# put selection here
selection = (2, 3, '050')

# build chart generated data versus historical data
predicted = repo.predict(selection, 30)
historical, sd, ed = repo.history(selection, 30)
title_common = " [%4d-%02d-%02d %4d-%02d-%02d]" \
          % (sd.year, sd.month, sd.day, ed.year, ed.month, ed.day)
title_common += " \nsex: %d, age category: %d, sline: '%s'" % selection
plt.title("Patients number by day" + title_common)
# plt.plot([len(ad) for ad in predicted], 'ro', [len(ad) for ad in historical], 'bx')
f1, = plt.plot([len(ad) for ad in predicted], 'ro', label='model')
f2, = plt.plot([len(ad) for ad in historical], 'bx', label='history')
plt.legend(handles=[f1, f2])
plt.show()

# build patients number freqs chart
plt.title("Patients number freqs" + title_common)
f1, = plt.plot(sorted([len(ad) for ad in predicted]), 'ro', label='model')
f2, = plt.plot(sorted([len(ad) for ad in historical]), 'bx', label='history')
plt.axis([0, 35, -1, 7])
plt.legend(handles=[f1, f2])
plt.show()

# build rlos freqs chart
rlos_predicted = sorted([p.rlos if p.rlos > 0 else 1 for ps in predicted for p in ps])
rlos_historical = sorted([p.rlos for ps in historical for p in ps])
plt.title("Rlos freqs" + title_common)
f1, = plt.plot(rlos_predicted, 'ro', label='model')
f2, = plt.plot(rlos_historical, 'bx', label='history')
plt.axis([0, 20, -1, 10])
plt.legend(handles=[f1, f2])
plt.show()


def metric(list):
    if len(list) == 0:
        return 0
    result = 0
    for x in list: result += x
    return result

# # build diff chart
# n_iter = 100
# model = []
# historic = []
# for i in xrange(n_iter):
#     predicted = repo.predict(selection, 30)
#     historical, sd, ed = repo.history(selection, 30)
#
#     rlos_predicted = metric([p.rlos if p.rlos > 0 else 1 for ps in predicted for p in ps])
#     rlos_historical = metric([p.rlos for ps in historical for p in ps])
#
#     # z = float(max(rlos_historical, rlos_predicted))
#     # rlos_historical = float(rlos_historical) / z
#     # rlos_predicted = float(rlos_predicted) / z
#
#     model.append(rlos_predicted)
#     historic.append(rlos_historical)
#     # print 'Add new point (%s, %s)' % (model[-1], historic[-1])
#
# model = sorted(model)
# historic = sorted(historic)
#
# plt.title('Difference between predicted and historic data')
# plt.xlabel('model')
# plt.ylabel('real')
# plt.plot(historic, 'bx', label='history')
# plt.plot(model, 'ro', label='model')
# plt.show()




