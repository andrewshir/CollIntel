import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn.metrics import log_loss
from sklearn.ensemble import RandomForestClassifier


working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week5\\"
df = pd.read_csv(filepath_or_buffer=working_path + "gbm-data.csv")

X = df.iloc[:, 1:].as_matrix()
y = df.iloc[:, 0].as_matrix()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8, random_state=241)

cf = RandomForestClassifier(n_estimators=36, random_state=241)
cf.fit(X_train, y_train)
y_pred = cf.predict_proba(X_test)

loss = log_loss(y_test, y_pred)

print loss
