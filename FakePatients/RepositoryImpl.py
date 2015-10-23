__author__ = 'Andrew'
from Repository import Repository
from Repository import DistrInfo
from FakePatients import get_patients_freq
import scipy.stats as stats


repo = Repository()
# Cardiology 35-50
repo.add_rvs((2, 3, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.17, size=x), 0.14))
# Cardiology 50-70
repo.add_rvs((2, 4, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.17, size=x), 0.5 ))
# Cardiology 50-70
repo.add_rvs((3, 4, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.17, size=x), 0.5 ))
# Urological Surgery 50-70
repo.add_rvs((2, 4, '387'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.17, size=x), 0.5 ))
# Urological Surgery 50-70
repo.add_rvs((3, 4, '387'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.17, size=x), 0.5 ))

print "Predicted"
print repo.predict((2, 3, '050'), 30)
print "Historic 1"
list, sd, ed = repo.history((2, 3, '050'), 30)
print list
print sd
print ed

print
print "Historic 2"
list, sd, ed = repo.history((2, 3, '050'), 30)
print list
print sd
print ed



# for tuple, prob in get_patients_freq().items():
#     print tuple, prob


