import pandas as pd
import numpy as np
import time


def load_df():
    """Loads data from original CSV file, remove unnecessary columns"""
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
    drg_list.sort()
    df = df.copy()

    # make separate feature for each DRG value
    for drg in drg_list:
        df["DRG_" + drg] = 0
        # use 0.5 because we will have 2 * 0.5 in case of different DRG
        df.loc[df['DRGG3'] == drg, "DRG_" + drg] = 0.5

    # parse date
    df['ADMIT_DATE'] = df['ADMIT_DATE'].map(lambda str_date:
                                            time.strptime(str_date, "%Y-%m-%d"))

    # use sqrt function to make accent on age difference for small ages
    df['AGE'] = df['AgeInYears'].map(lambda a: np.sqrt(float(a) / 12))
    df = df.drop(['DRGG3', 'AgeInYears'], axis=1)

    return df


def norm_values(df, col_date_name='ADMIT_DATE'):
    """Normalize numeric values to [0, 1]"""
    norms = {}
    for col in df.columns:
        if col == col_date_name:
            continue

        max = float(df[col].max())
        min = float(df[col].min())
        delta = max - min

        if delta == 0.0:
            # all values are equal, use this common value
            df[col] = min
        else:
            # transform to [0, 1]
            df[col] = df[col].map(lambda x: (float(x) - min) / delta)

        norms[col] = (min, max, delta)
    return norms


data = load_df()
data = transform_df(data)
norms = norm_values(data)
