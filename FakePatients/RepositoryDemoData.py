__author__ = 'Andrew'
import csv
from Repository import Repository
from Repository import DistrInfo
from FakePatients import working_path
import scipy.stats as stats
import matplotlib.pyplot as plt
import math

# print get_patients_freq()

repo = Repository()

repo.add_age_distr('050', lambda count: [18 if x < 18 else 103 if x > 103 else int(round(x))
                                     for x in stats.norm.rvs(loc=70.0, scale=16, size=count)])

# Cardiology <35
repo.add_patients_count_distr((2, 2, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.1, size=x), 0.7))
repo.add_rlos_distr((2, 2, '050'),
                    lambda count: [1 if x < 1 else int(math.floor(x)) for x in stats.expon.rvs(scale=2.0, size=count)])

# Cardiology 35-50
repo.add_patients_count_distr((2, 3, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.17, size=x), 0.14))
repo.add_rlos_distr((2, 3, '050'),
                    lambda count: [1 if x < 1 else int(math.floor(x)) for x in stats.expon.rvs(scale=2.0, size=count)])

# Cardiology 50-70
repo.add_patients_count_distr((2, 4, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.46, size=x), 0.45))
repo.add_rlos_distr((2, 4, '050'),
                    lambda count: [1 if x < 1 else int(math.floor(x)) for x in stats.expon.rvs(scale=2.2, size=count)])

# Cardiology >70
repo.add_patients_count_distr((2, 5, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.6, size=x), 0.53))
repo.add_rlos_distr((2, 5, '050'),
                    lambda count: [1 if x < 1 else int(math.floor(x)) for x in stats.expon.rvs(scale=4.3, size=count)])

# Cardiology <35
repo.add_patients_count_distr((3, 2, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.05, size=x), 0.05))
repo.add_rlos_distr((3, 2, '050'),
                    lambda count: [1 if x < 1 else int(math.floor(x)) for x in stats.expon.rvs(scale=1.8, size=count)])

# Cardiology 35-50
repo.add_patients_count_distr((3, 3, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.05, size=x), 0.09))
repo.add_rlos_distr((3, 3, '050'),
                    lambda count: [1 if x < 1 else int(math.floor(x)) for x in stats.expon.rvs(scale=2.3, size=count)])

# Cardiology 50-70
repo.add_patients_count_distr((3, 4, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.3, size=x), 0.336))
repo.add_rlos_distr((3, 4, '050'),
                    lambda count: [1 if x < 1 else int(math.floor(x)) for x in stats.expon.rvs(scale=2.5, size=count)])

# Cardiology 50-70
repo.add_patients_count_distr((3, 5, '050'), DistrInfo(lambda x: stats.poisson.rvs(mu=2.0, size=x), 0.63))
repo.add_rlos_distr((3, 5, '050'),
                    lambda count: [1 if x < 1 else int(math.floor(x)) for x in stats.expon.rvs(scale=6.0, size=count)])

# Urological Surgery <35
repo.add_patients_count_distr((2, 2, '387'), DistrInfo(lambda x: stats.poisson.rvs(mu=1.16, size=x), 0.22))

def run_once(selection):
    print "Model"
    predicted = repo.predict_patient_flow(selection, 30)
    for d in predicted:
        if len(d) != 0:
            for p in d:
                print str(p),
            print

    print
    historical, sd, ed = repo.history(selection, 30)
    print "Historical from %4d-%02d-%02d to %4d-%02d-%02d" % (sd.year, sd.month, sd.day, ed.year, ed.month, ed.day)
    for d in historical:
        if len(d) != 0:
            for p in d:
                print str(p),
            print


def generate_data(model_number=1, historic_number=1):
    result = []
    models_counter = 1

    sline = '050'
    for sex in [2, 3]:
        for age in [2,3,4,5]:

            for i in range(model_number):
                predicted = repo.predict_patient_flow((sex, age, sline), 30)
                for day in predicted:
                    for a in day:
                        id = "M%02d" % models_counter
                        result.append((id, a.date, a.sex, a.age, a.sline, a.rlos))
                models_counter += 1

            for i in range(historic_number):
                historical, sd, ed = repo.history((sex, age, sline), 30)
                for day in historical:
                    for a in day:
                        id = "H[%4d-%02d-%02d:%4d-%02d-%02d]" % (sd.year, sd.month, sd.day, ed.year, ed.month, ed.day)
                        result.append((id, a.date, a.sex, a.age, a.sline, a.rlos))
    return result

def create_file(filename='demo.csv'):
    data = generate_data()
    file = working_path + filename
    with open(file, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['DATASET', 'DATE', 'SEX', 'AGE', 'SL', 'LOS'])

        for row in data:
            writer.writerow(row)

# put selection here
# run_once((3, 4, '050'))

# print generate_data()
create_file('demo1.csv')