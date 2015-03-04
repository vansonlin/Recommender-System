__author__ = 'vanson'

'''
Refer to AllClicksInBuyingSession.txt
Construct TimeCompareForItemInBuyingSession.txt
'''

import pandas as pd
import numpy as np
import time

dr = "yoochoose-data/"
dfBuying = pd.read_csv(dr + "AllClicksInBuyingSession.txt", index_col=0 , engine='c', header=0, parse_dates=[6], nrows=2000)
dfBuying = dfBuying.drop(dfBuying.columns[[0,2]], 1) # remove category, price
sessionList_buying = np.genfromtxt(dr + "sessionList_buying.txt", dtype=int)
gb = dfBuying.groupby("sessionID")

def get_item_duration(df):
    # skip this session if all clicked items are bough, no time duration for un-bought item
    bought_items = df[df.buy == True].itemID.unique()
    if len(df.itemID.unique()) == len(bought_items): return

    itemID_series = df.itemID.values
    timestamp_series = df.timestamp.values
    time_duration = {}  # ns
    for i in range(len(df) - 1):
        if (time_duration.has_key(itemID_series[i])):  # if item is there
            time_duration[itemID_series[i]] += timestamp_series[i + 1] - timestamp_series[i]
        else:  # if unseen item
            time_duration[itemID_series[i]] = timestamp_series[i + 1] - timestamp_series[i]
    # extract longest time for non-bought item
    max_t = -1
    key_unbought = -1
    for key in time_duration.keys():
        if (not key in bought_items):
            if (time_duration[key]) > max_t:
                max_t = time_duration[key]
                key_unbought = key
    # extract time for each bought item, and write each line
    for key in bought_items:
        f.write("%s " % df.sessionID.unique()[0])
        f.write("%s " % key)  # bought itemID
        f.write("%s " % key_unbought)  # longest un-bought itemID
        f.write("%s " % (float(time_duration[key]) / pow(10, 9)))
        f.write("%s\n" % (float(max_t) / pow(10, 9)))

n = 1.
f = open("TimeCompareForItemInBuyingSession.txt", "w")
size = len(sessionList_buying) * 1.
t = time.time()
for i, j in gb:  # i = group name, j = group content
    if (n % 1000 == 0): print str(round(n*100 / size, 2)) + "% completed, Time Cost: " + str(time.time() - t)
    get_item_duration(j)
    n += 1
f.close()
print "All done"

