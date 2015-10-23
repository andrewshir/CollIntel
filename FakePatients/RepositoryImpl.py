__author__ = 'Andrew'
from Repository import Repository
from Repository import DistrInfo
from FakePatients import get_patients_freq
import scipy.stats as stats
import matplotlib.pyplot as plt


repo = Repository()
# Cardiology 35-50
repo.add_rvs((2, 3, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.17, size=x), 0.14))
# Cardiology 50-70
repo.add_rvs((2, 4, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.46, size=x), 0.45))
# Cardiology 50-70
repo.add_rvs((3, 4, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.3, size=x), 0.336))
# Urological Surgery 50-70
repo.add_rvs((2, 4, '387'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.44, size=x), 0.267))
# Urological Surgery 50-70
repo.add_rvs((3, 4, '387'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.17, size=x), 0.08))


# put selection here
selection = (2, 4, '050')

# build chart generated data versus historical data
predicted = repo.predict(selection, 30)
historical, sd, ed = repo.history(selection, 30)
plt.title("Generated data vs data from %4d-%02d-%02d to %4d-%02d-%02d"
          % (sd.year, sd.month, sd.day, ed.year, ed.month, ed.day))
plt.plot(predicted, 'ro', historical, 'bx')
plt.show()

# build freqs chart
plt.title("Generated data vs data from %4d-%02d-%02d to %4d-%02d-%02d"
          % (sd.year, sd.month, sd.day, ed.year, ed.month, ed.day))
plt.plot(sorted(predicted), 'ro', sorted(historical), 'bx')
plt.axis([0, 35, -1, 7])
plt.show()


# for tuple, prob in get_patients_freq().items():
#     print tuple, prob


