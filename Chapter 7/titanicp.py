import numpy as np
import pandas as pd
from sklearn.preprocessing import Imputer

work_path = 'C:\\Users\Andrew\\Source\\Repos\\CollIntel\\Chapter 7\\'


def load_train_data():
    df = pd.DataFrame.from_csv(work_path + 'train.csv')
    del df['Name']
    del df['Ticket']
    del df['Cabin']
    df = df[df['Embarked'].notnull()]
    arr = df.values

    x = np.transpose([arr[:, 3]])
    imp = Imputer(missing_values='NaN', strategy='median', copy=True)
    x = imp.fit_transform(x)
    arr[:, 3] = x[:, 0]
    return arr

X = load_train_data()
print X
print X[:, 3]