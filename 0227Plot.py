__author__ = 'vanson'
from scipy import stats
import numpy as np

dr = "associatedResult/"
f = open(dr + "TimeCompareForItemInBuyingSession.txt", "r")
for i in range(30):
    f.readline()

# get all records
time_buying = []
time_noBuying = []
line = f.readline()
while(len(line) > 1):
    line = line[:-1].split()
    time_buying.append(float(line[3]))
    time_noBuying.append(float(line[4]))
    line = f.readline()

# All records
X = time_buying
Y = time_noBuying
print len(X)
# len =  773687
print np.mean(X)
print np.mean(Y)
print stats.ttest_rel(X, Y) # calculate p-value
# mean of time_buying: 365.8405
# mean of time_noBuying: 432.1699
# t-test: -77.437168
# t-test: 2081.38757 (might be wrong)
# p-value: 0.0

################################################
dr = "associatedResult/"
f = open(dr + "TimeCompareForItemInBuyingSession.txt", "r")
for i in range(30):
    f.readline()

# get the first record for each session
time_buying = []
time_noBuying = []
line = f.readline()
s = 0
while(len(line) > 1):
    line = line[:-1].split()
    if (s != int(line[0])): # new session starts
        s = int(line[0])
        time_buying.append(float(line[3]))
        time_noBuying.append(float(line[4]))
    line = f.readline()

X = time_buying
Y = time_noBuying
# one record for each session (first record in each session)
print len(X)
# len = 341391
print np.mean(time_buying)
print np.mean(time_noBuying)
print stats.ttest_rel(X, Y) # calculate p-value
# mean of time_buying: 482.4730
# mean of time_noBuying: 424.964
# t-test: 39.931484
# p-value: 0.0

################################################
dr = "associatedResult/"
f = open(dr + "TimeCompareForItemInBuyingSession.txt", "r")
for i in range(30):
    f.readline()

# get the records with longest time on buying item for each session
time_buying = []
time_noBuying = []
line = f.readline()
s = 0
max_buying = 0
max_noBuying = 0
while(len(line) > 1):
    line = line[:-1].split()
    if (s != int(line[0])): # new session starts
        s = int(line[0])
        time_buying.append(max_buying)
        time_noBuying.append(max_noBuying)
        max_buying = float(line[3])
        max_noBuying = float(line[4])
        line = f.readline()
        continue
    if (s ==  int(line[0])): # new record in same session
        if (float(line[3]) > max_buying):
            max_buying = float(line[3])
            max_noBuying = float(line[4])
        line = f.readline()
        continue
time_buying.append(max_buying)
time_noBuying.append(max_noBuying)
time_buying = time_buying[1:] # remove the first item
time_noBuying = time_noBuying[1:] # remove the first item

X = time_buying
Y = time_noBuying
# one record for each session (record with longest time in buying item)
print len(X)
# len = 341391
print np.mean(time_buying)
print np.mean(time_noBuying)
print stats.ttest_rel(X, Y) # calculate p-value
# mean of time_buying: 643.7214
# mean of time_noBuying: 424.9648
# t-test: 146.439396
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

plt.plot(X,fitX, label = "Time for Bought Item, mean: " + str(round(np.mean(X), 3)) + ", std: " + str(round(np.std(X), 3))) # longest
plt.plot(Y,fitY, label = "Longest time for unpurchased Item, mean: " + str(round(np.mean(Y), 3)) + ", std: " + str(round(np.std(Y), 3))) # second longest
plt.xlim([0,2500])
plt.legend()
# plt.hist(h,normed=True)      #use this to draw histogram of your data
plt.xlabel("Time Spent distribution for item view (s)")
plt.ylabel("Probability")
plt.title("PDF of Time Spent on Viewed Item. (Longest Records, Bought and Longest nonPurchased). T-Test:149.439")
plt.show()

