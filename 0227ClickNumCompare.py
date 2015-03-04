__author__ = 'vanson'
import time

dr = "associatedResult/"
# # re-construct ClickNumTable_buying.txt
# filename = "ClickNumTable_buying.txt"
# f = open(dr + filename)
# s = ""
# for i in range(5):
#     s += f.readline()
#
# content = []
# line = f.readline()
# while (len(line) > 1):
#     content.append([int(line.split(",")[0]), line])
#     line = f.readline()
#
# from operator import itemgetter
# content = sorted(content, key=itemgetter(0))
# f.close()
# f = open("ClickNumTable_buying2.txt", "w")
# f.write(s)
# for i in content:
#     f.write(i[1])
# f.close()

#############################################
# All Records for buying session
# Draw distribution about number of clicks on buying item and most popular non-buying items
f = open(dr + "clickForItemDistribution/" + "ClickNumTable_buying.txt", "r")
for i in range(5):
    f.readline()

click_buying = []
click_noBuying = []
line = f.readline()
while(len(line) > 1):
    line = line[:-1].split(",")
    if (len(line) < 5):
        line = f.readline()
        continue
    click_buying.append(int(line[2]))
    click_noBuying.append(int(line[4]))
    line = f.readline()
f.close()

X = click_buying
Y = click_noBuying

from scipy import stats
import numpy as np
# Buying (clicks of bought item, clicks of most popular unpurchased item)
print len(X)
print np.mean(X)
print np.mean(Y)
print stats.ttest_rel(X, Y) # calculate p-value
# len = 773687
# mean of click_buying: 2.71214
# mean of click_noBuying: 1.49323
# t-test: 811.57576
# p-value: 0.0

#############################################
# One Record (first one) for each buying session
# Draw distribution about number of clicks on buying item and most popular non-buying items
f = open(dr + "clickForItemDistribution/" + "ClickNumTable_buying.txt", "r")
for i in range(5):
    f.readline()

click_buying = []
click_noBuying = []
line = f.readline()
sessionID = 0
while(len(line) > 1):
    line = line[:-1].split(",")
    if (len(line) < 5):
        line = f.readline()
        continue
    if (sessionID != int(line[0])): # found first record in that session
        click_buying.append(int(line[2]))
        click_noBuying.append(int(line[4]))
        sessionID = int(line[0])
    line = f.readline()
f.close()

X = click_buying
Y = click_noBuying

from scipy import stats
import numpy as np
# Buying (clicks of bought item, clicks of most popular unpurchased item)
# First record in each buying session
print len(X)
print np.mean(X)
print np.mean(Y)
print stats.ttest_rel(X, Y) # calculate p-value
# len = 341391
# mean of click_buying: 2.8891
# mean of click_noBuying: 1.4619
# t-test: 573.4723
# p-value: 0.0


#############################################
# One Record for each no-Buying session
# Draw distribution about number of clicks on most and second popular un-purchased item
f = open(dr + "clickForItemDistribution/" + "ClickNumTable_noBuying.txt", "r")
for i in range(5):
    f.readline()

click_f = []
click_s = []
line = f.readline()
sessionID = 0
while(len(line) > 1):
    line = line[:-1].split(",")
    if (len(line) < 5):
        line = f.readline()
        continue
    click_f.append(int(line[2]))
    click_s.append(int(line[4]))
    line = f.readline()
f.close()

X = click_f
Y = click_s

from scipy import stats
import numpy as np
# Buying (clicks of bought item, clicks of most popular unpurchased item)
# First record in each buying session
print len(X)
print np.mean(X)
print np.mean(Y)
print stats.ttest_rel(X, Y) # calculate p-value
# len = 6349949
# mean of click_buying: 1.4306
# mean of click_noBuying: 1.1172
# t-test: 1141.8726
# p-value: 0.0


###########################
#### Plot Distribution ####
###########################

import matplotlib.pyplot as plt
import scipy.stats as stats
X.sort()
Y.sort()

fitX = stats.norm.pdf(X, np.mean(X), np.std(X))  #this is a fitting indeed
fitY = stats.norm.pdf(Y, np.mean(Y), np.std(Y))  #this is a fitting indeed

plt.plot(X,fitX, label = "Most Popular Un-Purchased Bought Item, mean: " + str(round(np.mean(X), 1)) + ", std: " + str(round(np.std(X), 1))) # longest
plt.plot(Y,fitY, label = "Second Popular Un-Purchased Item, mean: " + str(round(np.mean(Y), 1)) + ", std: " + str(round(np.std(Y), 1))) # second longest
plt.xlim([1,7])
plt.legend()
# plt.hist(h,normed=True)      #use this to draw histogram of your data
plt.xlabel("N of Click Distribution for Items (s)")
plt.ylabel("Probability")
plt.title("PDF of N of Clicks on Items. (Most and Second Popular Un-Purchased Items, T-Test: 1141.9")
plt.show()
