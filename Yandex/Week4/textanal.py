import pandas as pd
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
from sklearn.linear_model import Ridge

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week4\\"
df = pd.read_csv(filepath_or_buffer=working_path + "salary-train.csv")

df['LocationNormalized'].fillna('nan', inplace=True)
df['ContractTime'].fillna('nan', inplace=True)
df['FullDescription'] = df['FullDescription'].map(lambda x: x.lower())
df['LocationNormalized'] = df['LocationNormalized'].map(lambda x: x.lower())
df['ContractTime'] = df['ContractTime'].map(lambda x: x.lower())
df['FullDescription'] = df['FullDescription'].replace('[^a-zA-Z0-9]', ' ', regex=True)

vectorizer = TfidfVectorizer(min_df=5)
full_descr = vectorizer.fit_transform(df['FullDescription'].as_matrix())
dict_vectorizer = DictVectorizer()

time_and_loc = dict_vectorizer.fit_transform(df[['LocationNormalized', 'ContractTime']].to_dict('records'))
train = hstack((full_descr, time_and_loc))
y = df['SalaryNormalized'].as_matrix()

ridge = Ridge(alpha=1.0)
ridge.fit(train, y)


dft = pd.read_csv(filepath_or_buffer=working_path + "salary-test-mini.csv")
dft['LocationNormalized'].fillna('nan', inplace=True)
dft['ContractTime'].fillna('nan', inplace=True)
dft['FullDescription'] = dft['FullDescription'].map(lambda x: x.lower())
dft['LocationNormalized'] = dft['LocationNormalized'].map(lambda x: x.lower())
dft['ContractTime'] = dft['ContractTime'].map(lambda x: x.lower())
dft['FullDescription'] = dft['FullDescription'].replace('[^a-zA-Z0-9]', ' ', regex=True)
full_descr = vectorizer.transform(dft['FullDescription'].as_matrix())
time_and_loc = dict_vectorizer.transform(dft[['LocationNormalized', 'ContractTime']].to_dict('records'))
test = hstack((full_descr, time_and_loc))

print ridge.predict(test)




