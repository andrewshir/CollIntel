__author__ = 'Andrew'
from FakePatients import split_age
from FakePatients import get_empty_combinations
import random

class Repository(object):
    def __init__(self):
        self.empty = set(get_empty_combinations())
        self.rvs = {}

    def add_rvs(self, (sex, age, sline), sline_info):
        self.rvs[(sex, age, sline)] = sline_info

    def predict(self, (sex, age, sline), days=30):
        """Generates patients flow for selected combination of (sex, age, sline)"""
        if (sex, age, sline) in self.empty:
            raise RuntimeError('Desired combination of sex %d, age %d, sline %s is missed in historical data'
                               % (sex, age, sline))

        if (sex, age, sline) not in self.rvs:
            raise NotImplementedError('Desired combination of sex %d, age %d, sline %s is not implemented'
                               % (sex, age, sline))

        sline_info = self.rvs[(sex, age, sline)]
        patients_flow = sline_info.rvs(days).tolist()
        result = []
        for iday in range(days):
            if sline_info.prob == 1.0 or random.random() <= sline_info.prob:
                v = patients_flow.pop()
                result.append(1 if v == 0 else v)
            else:
                result.append(0)
        return result

class DistrInfo(object):
    """Describes sline patient count distribution"""

    def __init__(self, rvs=None, prob=1.0):
        # function to get number of patient with this sline per day
        self.rvs = rvs
        # probability of admittance of patient with this sline
        self.prob = prob
