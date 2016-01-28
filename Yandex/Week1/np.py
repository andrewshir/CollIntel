import numpy as np

matrix = np.random.normal(1, 10, (1000, 50))
print matrix
shape = np.shape(matrix)
print shape

mean = np.mean(matrix, axis=0)
std = np.std(matrix, axis=0)
matrix_norm = (matrix - mean) / std
print matrix_norm

summ = np.sum(matrix, axis=1)
bool_matrix = summ > 10
print np.nonzero(bool_matrix)[0]

m1 = np.identity(3)
m2 = np.identity(3)
print np.vstack((m1, m2))
