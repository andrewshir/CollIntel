import pandas as pd

data = pd.read_csv(r'C:\Users\Andrew\Source\Repos\CollIntel\Yandex\Week1\titanic.csv', index_col='PassengerId')

# 1
# print data['Sex'].value_counts()

# 2
len(data['Survive'] == 1)




