import pandas as pd
import numpy as np
import datetime
import random
from sklearn.neighbors import KernelDensity
from sklearn.neighbors import DistanceMetric
import matplotlib.pyplot as plt

drg_list = ['302', '403', '201', '560', '347', '098', '114', '249', '313',
            '861', '194', '342', '073', '540', '221', '137', '241', '175',
            '422', '301', '513', '383', '144', '612', '500', '254', '180',
            '364', '225', '315', '341', '138', '385', '468', '351', '320',
            '722', '721', '693', '139', '190', '425', '314', '563', '092',
            '501', '463', '951', '566', '310', '363', '228', '248', '862',
            '316', '097', '243', '304', '134', '222', '042', '361', '089',
            '026', '093', '197', '263', '651', '308', '812', '423', '531',
            '057', '517', '544', '518', '663', '317', '691', '813', '441',
            '283', '482', '226', '460', '404', '952', '140', '207', '850',
            '384', '284', '173', '047', '860', '045', '192', '244', '111',
            '247', '171', '466', '519', '346', '723', '113', '024', '446',
            '760', '711', '240', '751', '561', '058', '465', '280', '227',
            '532', '082', '252', '281', '754', '758', '710', '143', '130',
            '245', '199', '044', '775', '049', '242', '483', '053', '282',
            '191', '115', '220', '420', '204', '640', '142', '048', '141',
            '510', '681', '445', '362', '054', '136', '205', '229', '023',
            '461', '043', '264', '340', '791', '070', '660', '349', '176',
            '312', '224', '614', '621', '442', '724', '484', '135', '694',
            '530', '545', '041', '950', '756', '815', '514', '052', '200',
            '626', '720', '546', '421', '169', '170', '381', '661', '772',
            '622', '930', '564', '512', '309', '447', '443', '343', '121',
            '424', '774', '203', '080', '776', '051', '757', '755', '253',
            '344', '223', '480', '198', '911', '246', '740', '251', '750',
            '816', '196', '380', '004', '680', '110', '481', '639', '565',
            '636', '193', '133', '462', '305', '177', '279', '811', '542',
            '844', '863', '046', '633', '056', '955', '634', '040', '759',
            '894', '005', '912', '206', '120', '055', '843', '752', '541',
            '382', '753', '095', '650', '401', '593', '581', '050', '260',
            '625', '174', '321', '692', '261', '091', '773', '613', '262',
            '690', '511', '770', '405', '608', '623', '132', '607', '603',
            '589', '580', '890', '131', '003']


def load_df():
    """Loads data from original CSV file, remove unnecessary columns, filter out unrelevant data"""
    working_path = r'C:\Users\Andrew\Source\Repos\CollIntel\FakePatients2' + "\\"
    df = pd.read_csv(working_path + 'FakePatients.csv')
    df = df.drop(['PERIOD', 'Visit_Id', 'DIS_DATE', 'BILLED_LOS', 'REALIZED_LOS',
                  'STAY_TYPE', 'ISDIED', 'NUM_DDX_TOTAL', 'NUM_PROC_TOTAL'], axis=1)
    df = df.loc[df['DRGG3'] != 'MMM', :]
    df = df.loc[df['DRGG3'] != 'DDD', :]
    df = df.loc[df['DRGG3'] != 'UUU', :]
    df = df.loc[df['DRGG3'].notnull(), :]
    df = df.loc[df['AgeInYears'] != 0, :]
    return df


def transform_df(df):
    """Transform column values"""
    drg_list.sort()
    df = df.copy()

    # map DRG to numbers
    df['DRG'] = df['DRGG3'].map(lambda d: drg_list.index(d))

    # parse date
    df['ADMIT_DATE'] = df['ADMIT_DATE'].map(lambda str_date:
                                            datetime.datetime.strptime(str_date, "%Y-%m-%d"))

    # cut 2010 and earlier data, because of data incompleteness
    df = df.loc[df['ADMIT_DATE'] >= datetime.date(2011, 1, 1), :]

    # rename columns
    df['AGE'] = df['AgeInYears']
    df['SOI'] = df['SOIG3']

    df = df.drop(['DRGG3', 'AgeInYears', 'SOIG3'], axis=1)

    return df


def patient_metric(p1, p2):
    result = 0.0
    # SEX with x2 weight
    result += float(abs(p1[0] - p2[0])) * 2
    # DRG
    result += 0.0 if p1[1] == p2[1] else 1.0
    # AGE
    # it seems this approach cannot be used, because it might break
    # identity property: d(x, y) = 0 if and only if x == y
    # this needs to be checked
    # result += float(abs(p1[3] - p2[3])) / np.mean([p1[3], p2[3]])
    # so use sqrt instead
    result += abs(np.sqrt(float(p1[2]) / 12) - np.sqrt(float(p2[2]) / 12))
    # SOI
    result += float(abs(p1[3] - p2[3])) / 4
    return result


def get_patient_numbers(df, length_in_days=30):
    min_date = df['ADMIT_DATE'].min()
    max_date = df['ADMIT_DATE'].max() - datetime.timedelta(days=length_in_days)
    total_delta = max_date - min_date

    # we will take periods with some overlapping
    periods_count = int(round(total_delta.days / length_in_days * 1.2))
    result = []
    dates = [pd.to_datetime(d) for d in df['ADMIT_DATE'].values]
    for i in xrange(periods_count):
        period_start = min_date + datetime.timedelta(days=random.randint(0, total_delta.days))
        period_end = period_start + datetime.timedelta(days=length_in_days)
        count = 0
        for d in dates:
            if period_start <= d <= period_end:
                count += 1
        result.append(count)
    return result


def get_period_samples(df, num_samples=None, length_in_days=30):
    min_date = df['ADMIT_DATE'].min()
    max_date = df['ADMIT_DATE'].max() - datetime.timedelta(days=length_in_days)
    total_delta = max_date - min_date

    if num_samples is None:
        num_samples = int(round(total_delta.days / length_in_days))
    result = []
    for i in xrange(num_samples):
        period_start = min_date + datetime.timedelta(days=random.randint(0, total_delta.days))
        period_end = period_start + datetime.timedelta(days=length_in_days)
        result.append(df.loc[df['ADMIT_DATE'] >= period_start].loc[df['ADMIT_DATE'] <= period_end].values)

    return result


def train_patient_number_estimator(pat_numbers, bandwidth=1.0):
    """Define distribution of patients number"""
    X = [[x] for x in pat_numbers]
    estimator = KernelDensity(bandwidth=bandwidth, kernel='gaussian')
    estimator.fit(X)
    return estimator


def train_patient_flow_estimator(df, bandwidth=1.0):
    """Train density estimator based on patient metric"""
    X = df.drop(['ADMIT_DATE'], axis=1).values
    estimator = KernelDensity(bandwidth=bandwidth,
                              kernel='gaussian',
                              metric='pyfunc',
                              metric_params={'func': patient_metric})
    estimator.fit(X)
    return estimator


def discretize_estimated_sample(sample):
    """Create meaningful values from generated sample"""
    result = []
    for row in sample:
        result.append((
            2 if row[0] < 2.5 else 3,
            0 if row[1] < 0 else len(drg_list) - 1 if row[1] >= len(drg_list) else int(round(row[1])),
            0 if row[2] < 0 else 105 if row[2] > 105 else int(round(row[2])),
            0 if row[3] < 0 else 4 if row[3] >= 3.5 else int(round(row[3]))
        ))
    return result

data = load_df()
data = transform_df(data)

period_samples = get_period_samples(data, num_samples=3)
for period in period_samples:
    print period

# patient number for custom period
patient_numbers = get_patient_numbers(data)
patient_number_estimator = train_patient_number_estimator(patient_numbers)
for i in xrange(3):
    patient_numbers = get_patient_numbers(data)
    patient_numbers_gen = [int(round(x)) for x in
                           patient_number_estimator.sample(n_samples=len(patient_numbers)).flatten()]

    patient_number_hist_mean = int(np.round(np.mean(patient_numbers)))
    patient_number_hist_std = int(np.round(np.std(patient_numbers)))
    patient_number_gen_mean = int(np.round(np.mean(patient_numbers_gen)))
    patient_number_gen_std = int(np.round(np.std(patient_numbers_gen)))

    print "Iteration %s" % i
    print "Historic    Mean=%d Std=%d" % (patient_number_hist_mean, patient_number_hist_std)
    print "Generated   Mean=%d Std=%d" % (patient_number_gen_mean, patient_number_gen_std)



# patient flow estimation
patient_flow_estimator = train_patient_flow_estimator(data)
patient_flow_gen = patient_flow_estimator.sample(n_samples=5)
patient_flow_gen = discretize_estimated_sample(patient_flow_gen)
print patient_flow_gen






