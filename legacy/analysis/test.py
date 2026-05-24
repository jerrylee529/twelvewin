# coding=utf8

"""聚类算法实验脚本。

该文件读取本地 e:/sz50.csv 数据，尝试用 AffinityPropagation/KMeans 对样本做聚类，
并结合 e:/sz50_symbol.csv 输出聚类结果。属于临时实验代码，不参与主业务流程。
"""

__author__ = 'Administrator'


#x1 = np.array([1, 2, 3, 1, 5, 6, 5, 5, 6, 7, 8, 9, 9])
#x2 = np.array([1, 3, 2, 2, 8, 6, 7, 6, 7, 1, 2, 1, 3])
#x = np.array(list(zip(x1, x2))).reshape(len(x1), 2)

def main():
    import numpy as np
    import pandas as pd
    from sklearn.cluster import AffinityPropagation

    df = pd.read_csv("e:/sz50.csv")

    df = df.fillna(0.1)

    x = df.values

    print(np.isnan(x).any())

    print(x)

    # #############################################################################
    # Compute Affinity Propagation
    af = AffinityPropagation(affinity='precomputed').fit(x)
    cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    n_clusters_ = len(cluster_centers_indices)

    print('Estimated number of clusters: %d' % n_clusters_)
    print(labels)

    df = pd.read_csv("e:/sz50_symbol.csv")

    df.set_index('code', inplace=True)

    names = df['name']

    i = 0
    d = {}
    for name in names.values:
        label = str(labels[i])
        if label not in d:
            d[label] = []
        d[label].append(name)

        i += 1

    for key, values in d.items():
        names = u''
        for value in values:
            names += value
            names += ','
        print(key, names)


if __name__ == '__main__':
    main()
