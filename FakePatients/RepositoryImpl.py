__author__ = 'Andrew'
from Repository import Repository
from Repository import DistrInfo
import scipy.stats as stats


repo = Repository()
# Cardiology 35-50
repo.add_rvs((2, 3, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.17, size=x), 0.5))
# Cardiology 50-70
repo.add_rvs((2, 4, '050'), DistrInfo(lambda x: stats.poisson.cdf(x, mu=2) ))
# Cardiology 50-70
repo.add_rvs((3, 4, '050'), DistrInfo(lambda x: stats.poisson.cdf(x, mu=2) ))
# Urological Surgery 50-70
repo.add_rvs((2, 4, '387'), DistrInfo(lambda x: stats.poisson.cdf(x, mu=2) ))
# Urological Surgery 50-70
repo.add_rvs((3, 4, '387'), DistrInfo(lambda x: stats.poisson.cdf(x, mu=2) ))

print repo.predict((2, 3, '050'), 30)

