__author__ = 'vanson'

import numpy as np

item_list_old = np.genfromtxt("yoochoose-data/itemList.txt", dtype=int)
clustering_result = np.genfromtxt("clustering/ItemItemMatrix_1basedCSR_Probability.txt.clustering.100.txt", dtype=int)
new_order = np.genfromtxt("clustering/new_order.txt", dtype=int)
matrix_permuted = open("clustering/matrix_100_RowColumnPermuted.txt", "r").readlines()

matrix_original = open("associatedResult/ItemItemMatrix_1basedCSR_Probability.txt", "r").readlines()

# print size of each cluster from cluster -1 to cluster 9
for i in range(-1, 10, 1):
    print str(i) + ": " + str(sum(clustering_result == i))
# -1: 4772
# 0: 177
# 1: 205
# 2: 254
# 3: 398
# 4: 297
# 5: 220
# 6: 395
# 7: 295
# 8: 334
# 9: 334

# calculate size of the intent matrix, number of members in cluster 0 to 9
# 2909 items in cluster 0 - cluster 9
count = 0
for i in clustering_result:
    if i in range(10):
        count += 1

size_of_negative = sum(clustering_result == -1)
matrix_top_10_clusters = np.zeros([count, count]) # construct the intent matrix with zeros

i = 0 # row pointer
for row in matrix_permuted[size_of_negative+1: size_of_negative+1+count]:
    row = row[:-1]
    if (len(row) > 0):
        row = map(float, row.split(" "))
        for j in range(len(row)):
            if (j % 2 == 1 and row[j - 1] <= size_of_negative + count and row[j - 1] >= size_of_negative + 1): # if value , then j -1 refer to column index (1-based)
                matrix_top_10_clusters[i, row[j - 1] - size_of_negative-1] = row[j] # assign the real probability
                # matrix_top_10_clusters[i, row[j - 1] - size_of_negative-1] = 1 # assign all non-zero value as 1
    i += 1

import matplotlib.pylab as plt
# plt.matshow(matrix_top_10_clusters)
plt.imshow(matrix_top_10_clusters)
plt.colorbar()
plt.title("Permuted Matrix for top 10 clusters, probability")
fig = plt.gcf()
fig.set_size_inches(15,12)
plt.savefig("matrix_probability.png", dpi=200)
# plt.show()


