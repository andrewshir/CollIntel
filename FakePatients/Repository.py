__author__ = 'Andrew'
from FakePatients import split_age
from FakePatients import get_empty_combinations
from FakePatients import load_data_with_sline
from FakePatients import parse_datetime
from datetime import timedelta
import random

class Repository(object):
    def __init__(self):
        self.all_data = load_data_with_sline()
        self.empty = set(get_empty_combinations(self.all_data))
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

    def history(self, (sex, age, sline), days=30):
        """Return historical data for selected combination of (sex, age, sline)"""
        start_date = None
        end_date = None
        hist_data = {}
        for row in self.all_data:
            admit_date = row[2]
            agef = split_age(int(row[9]))
            sexf = int(row[10])
            slinef = row[14]

            if sline is None:
                continue
            if len(admit_date) == 0:
                continue

            if (sex, age, sline) != (sexf, agef, slinef):
                continue
            datetime = parse_datetime(admit_date)

            start_date = datetime if start_date is None or datetime < start_date else start_date
            end_date = datetime if end_date is None or datetime > end_date else end_date
            hist_data.setdefault(datetime, 0)
            hist_data[datetime] += 1

        start_day = random.randint(0, (end_date - start_date).days)
        end_day = start_day + days
        # print start_date
        # print end_date
        # print start_date + timedelta(start_day)
        # print start_date + timedelta(end_day)

        result = []
        for day in range(start_day, end_day + 1):
            day_dt = start_date + timedelta(day)
            result.append(hist_data[day_dt] if day_dt in hist_data else 0)

        return result, start_date + timedelta(start_day), start_date + timedelta(end_day)


class DistrInfo(object):
    """Describes sline patient count distribution"""

    def __init__(self, rvs=None, prob=1.0):
        # function to get number of patient with this sline per day
        self.rvs = rvs
        # probability of admittance of patient with this sline
        self.prob = prob
