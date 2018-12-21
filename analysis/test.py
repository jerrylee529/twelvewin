# coding=utf8

"""
测试文件
"""

__author__ = 'Administrator'


import numpy as np

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#x1 = np.array([1, 2, 3, 1, 5, 6, 5, 5, 6, 7, 8, 9, 9])
#x2 = np.array([1, 3, 2, 2, 8, 6, 7, 6, 7, 1, 2, 1, 3])
#x = np.array(list(zip(x1, x2))).reshape(len(x1), 2)

import pandas as pd

df = pd.read_csv("e:/sz50.csv")

df = df.fillna(0.1)

x = df.values

print np.isnan(x).any()

print x


'''
from sklearn.cluster import KMeans
kmeans=KMeans(n_clusters=8)   #n_clusters:number of cluster
kmeans.fit(x)
print kmeans.labels_


df = pd.read_csv("e:/sz50_symbol.csv", encoding='gbk')

df.set_index('code', inplace=True)

names = df['name']

i = 0
for name in names.values:
    print 'name: %s, label: %d' % (name, kmeans.labels_[i])
    i += 1

'''

from sklearn.cluster import AffinityPropagation
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs

# #############################################################################
# Generate sample data
'''
centers = [[1, 1], [-1, -1], [1, -1]]
X, labels_true = make_blobs(n_samples=300, centers=centers, cluster_std=0.5,
                            random_state=0)

print X
'''

# #############################################################################
# Compute Affinity Propagation
'''precomputed, euclidean'''
af = AffinityPropagation(affinity='precomputed').fit(x)
cluster_centers_indices = af.cluster_centers_indices_
labels = af.labels_

n_clusters_ = len(cluster_centers_indices)


print('Estimated number of clusters: %d' % n_clusters_)
print labels

df = pd.read_csv("e:/sz50_symbol.csv")

df.set_index('code', inplace=True)

names = df['name']

#print names

i = 0
d = {}
for name in names.values:
    if d.has_key(str(labels[i])):
        d[str(labels[i])].append(name)
    else:
        d[str(labels[i])] = []
        d[str(labels[i])].append(name)

    i += 1

for key, values in d.items():
    names = u''
    for value in values:
        names += value
        names += ','
    print key, names

'''
print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
print("Adjusted Rand Index: %0.3f"
      % metrics.adjusted_rand_score(labels_true, labels))
print("Adjusted Mutual Information: %0.3f"
      % metrics.adjusted_mutual_info_score(labels_true, labels))
print("Silhouette Coefficient: %0.3f"
      % metrics.silhouette_score(x, labels, metric='sqeuclidean'))
'''
