from skimage.io import imread
from skimage import img_as_float
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np


def psnr(K, M):
    mse = ((K - M) ** 2).mean()
    return 20*np.log10(1.0 / np.sqrt(mse))


working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Yandex\\Week6\\"

image = imread(working_path + 'parrots.jpg')
image_rgb = img_as_float(image)
# join first 2 dimensions
X = image_rgb.reshape(-1, image_rgb.shape[-1])

for num_clusters in xrange(2, 21):
    print "Number of clusters %d" % num_clusters

    c = KMeans(init='k-means++', random_state=241, n_clusters=num_clusters)
    c.fit(X)
    labels = c.labels_

    # define colors for clusters

    df = pd.DataFrame(X.copy())
    df['cl'] = labels
    for i in xrange(num_clusters):
        cluster_pixels = df['cl'] == i
        r_mean, g_mean, b_mean = df[cluster_pixels].iloc[:, 0:3].mean()
        df.ix[cluster_pixels, 0] = r_mean
        df.ix[cluster_pixels, 1] = g_mean
        df.ix[cluster_pixels, 2] = b_mean
    psnr_mean = psnr(df.iloc[:, 0:3].as_matrix(), X)
    print "PSNR (mean) %f" % psnr_mean

    df = pd.DataFrame(X.copy())
    df['cl'] = labels
    for i in xrange(num_clusters):
        r_med, g_med, b_med = df[cluster_pixels].iloc[:, 0:3].median()
        df.ix[cluster_pixels, 0] = r_med
        df.ix[cluster_pixels, 1] = g_med
        df.ix[cluster_pixels, 2] = b_med
    psnr_med = psnr(df.iloc[:, 0:3].as_matrix(), X)
    print "PSNR (med) %f" % psnr_med

    print


