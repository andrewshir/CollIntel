import pandas as pd
import numpy as np
from sklearn.decomposition import PCA

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week4\\"
df = pd.read_csv(filepath_or_buffer=working_path + "close_prices.csv")
X = df.iloc[:, 1:]

# pca = PCA(30)
# pca.fit_transform(X)
# print pca.explained_variance_ratio_

pca = PCA(10)
X = pca.fit_transform(X)
print pca.explained_variance_ratio_

# pca = PCA(0.9)
# pca.fit_transform(X)
# print pca.n_components_

f = X[:, 0]

dfdj = pd.read_csv(filepath_or_buffer=working_path + "djia_index.csv")
fdj = dfdj.iloc[:, 1].as_matrix()

cfp = np.corrcoef(x=f, y=fdj)

pca.components_[0, :]




