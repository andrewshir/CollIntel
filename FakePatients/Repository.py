__author__ = 'Andrew'
from FakePatients import split_age
from FakePatients import get_empty_combinations
from FakePatients import load_data_with_sline
from FakePatients import parse_datetime
from datetime import timedelta
import random

class Repository(object):
    def __init__(self, all_data=None):
        self.all_data = load_data_with_sline() if all_data is None else all_data
        self.empty = set(get_empty_combinations(self.all_data))
        self.patients_count_distr = {}
        self.rlos_distr = {}
        self.age_distr = {}

    def rvs_filtered(self, rvs_func, size, filter_func=None):
        if filter_func is None:
            return rvs_func(size)
        else:
            result = rvs_func(size)
            result = [x for x in result if filter_func(x)]
            delta = size - len(result)
            maxdelta = delta
            n_iter = 0
            while delta > 0:
                maxdelta = max(delta, maxdelta) + 5
                result = rvs_func(size + maxdelta)
                result = [x for x in result if filter_func(x)]
                delta = size - len(result)
                if n_iter > 1000:
                    raise RuntimeError("Too strong filtration condition")
                n_iter += 1
            return result[0:size]

    def add_patients_count_distr(self, (sex, age, sline), distr_info):
        self.patients_count_distr[(sex, age, sline)] = distr_info

    def add_rlos_distr(self, (sex, age, sline), rlos_function, rlos_filter_function=None):
        if rlos_filter_function is None:
            self.rlos_distr[(sex, age, sline)] = rlos_function
        else:
            self.rlos_distr[(sex, age, sline)] = \
                lambda size: self.rvs_filtered(rlos_function, size, rlos_filter_function)

    def add_age_distr(self, sline, age_function):
        self.age_distr[sline] = age_function

    def predict_patient_flow(self, (sex, age, sline), days=30):
        """Generates patients flow for selected combination of (sex, age, sline)"""
        if (sex, age, sline) in self.empty:
            raise RuntimeError('Desired combination of sex %d, age %d, sline %s is missed in historical data'
                               % (sex, age, sline))

        if (sex, age, sline) not in self.patients_count_distr:
            raise NotImplementedError('Patient flow for selection: sex %d, age %d, sline %s is not implemented'
                               % (sex, age, sline))

        if sline not in self.age_distr:
            raise NotImplementedError('Age distribution for sline %s is not implemented'
                               % sline)

        if (sex, age, sline) not in self.rlos_distr:
            raise NotImplementedError('RLos distribution for selection: sex %d, age %d, sline %s is not implemented'
                               % (sex, age, sline))

        rlos_flow_func = lambda: self.rlos_distr[(sex, age, sline)](100)
        rlos_flow = rlos_flow_func()
        age_flow_func = lambda: [a for a in self.age_distr[sline](500) if split_age(a) == age]
        age_flow = age_flow_func()
        sline_distr_info = self.patients_count_distr[(sex, age, sline)]
        patients_flow = sline_distr_info.rvs(days).tolist()

        result = []
        for iday in range(days):
            if sline_distr_info.prob == 1.0 or random.random() <= sline_distr_info.prob:
                pat_count = patients_flow.pop()
                admits = []
                #todo: move convertion from 0 to 1 to rvs function
                for p in xrange(1 if pat_count == 0 else pat_count):
                    admits.append(AdmitInfo(str(iday+1), sex, age_flow.pop(), sline, rlos_flow.pop()))
                    if len(rlos_flow) == 0:
                        rlos_flow = rlos_flow_func()
                    if len(age_flow) == 0:
                        age_flow = age_flow_func()

                result.append(admits)
            else:
                result.append([])
        return result

    def history(self, (sex, age, sline), days=30):
        """Return historical data for selected combination of (sex, age, sline)"""
        start_date = None
        end_date = None
        hist_data = {}
        for row in self.all_data:
            admit_date = row[2]
            agef_in_years = int(row[9])
            agef = split_age(agef_in_years)
            sexf = int(row[10])
            slinef = row[14]
            rlos = row[5]

            if sline is None:
                continue
            if len(admit_date) == 0:
                continue

            if len(rlos) == 0:
                continue

            if (sex, age, sline) != (sexf, agef, slinef):
                continue
            datetime = parse_datetime(admit_date)

            start_date = datetime if start_date is None or datetime < start_date else start_date
            end_date = datetime if end_date is None or datetime > end_date else end_date
            hist_data.setdefault(datetime, [])
            hist_data[datetime].append(AdmitInfo(admit_date, sex, agef_in_years, sline, int(rlos)))

        start_day = random.randint(0, (end_date - start_date).days)
        end_day = start_day + days
        # print start_date
        # print end_date
        # print start_date + timedelta(start_day)
        # print start_date + timedelta(end_day)

        result = []
        for day in range(start_day, end_day + 1):
            day_dt = start_date + timedelta(day)
            result.append(hist_data[day_dt] if day_dt in hist_data else [])

        return result, start_date + timedelta(start_day), start_date + timedelta(end_day)


class AdmitInfo(object):
    """Describes single patient admittance"""
    def __init__(self, date, sex, age, sline, rlos):
        self.date = date
        self.sex = sex
        self.age = age
        self.sline = sline
        self.rlos = rlos

    def get_age_category(self):
        return split_age(self.age)

    def __str__(self):
        return "%s(%d,%d,%s)rlos:%d" % (self.date, self.sex, self.age, self.sline, self.rlos)

class DistrInfo(object):
    """Describes sline patient count distribution"""

    def __init__(self, rvs=None, prob=1.0):
        # function to get number of patient with this sline per day
        self.rvs = rvs
        # probability of admittance of patient with this sline
        self.prob = prob
