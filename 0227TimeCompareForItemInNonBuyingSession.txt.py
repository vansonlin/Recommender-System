__author__ = 'vanson'
import pandas as pd
import numpy as np
import time

'''
Construct TimeCompareForItemInNonBuyingSession.txt

Each row is for each nonBuying session (session without buying action):
 -> sessionID, most popular item(most clicks in that session), # of clicks, second popular item, # of clicks...
'''
t = time.time()
dr = "yoochoose-data/"
dfNonBuying = pd.read_csv(dr + "AllClicksInNoBuyingSession.txt", index_col=0 , engine='c', header=0, parse_dates=[2], nrows=2000)
dfNonBuying = dfNonBuying.drop(dfNonBuying.columns[3], 1) # remove category
gb = dfNonBuying.groupby("sessionID")
print time.time() - t

def get_item_duration(df):
    # skip this session if unique item clicked are less than 2 (only 1 in other word)
    if len(df.itemID.unique()) < 2:
        return

    time_duration = {}
    itemID_series = df.itemID.values
    timestamp_series = df.timestamp.values
    for i in range(len(df) - 1):
        if (time_duration.has_key(itemID_series[i])): # if the itemID already exists
            time_duration[itemID_series[i]] += timestamp_series[i+1] - timestamp_series[i]
        else:  # if unseen item
            time_duration[itemID_series[i]] = timestamp_series[i + 1] - timestamp_series[i]
    max_f_t = -1 # the longest
    max_s_t = -2 # the second longest
    max_f_ID = 0
    max_s_ID = 0
    for key in time_duration.keys():
        if (time_duration[key] > max_f_t): # if max found
            max_s_t = max_f_t
            max_s_ID = max_f_ID
            max_f_t = time_duration[key]
            max_f_ID = key
            continue
        if (time_duration[key] > max_s_t):
            max_s_t = time_duration[key]
            max_s_ID = key
    if (max_s_ID == 0): return # if second longest time is not available
    f.write("%s " % df.sessionID.unique()[0])
    f.write("%s " % max_f_ID)  # longest itemID
    f.write("%s " % max_s_ID)  # second longest itemID
    f.write("%s " % (float(max_f_t) / pow(10, 9)))
    f.write("%s\n" % (float(max_s_t) / pow(10, 9)))

size = len(dfNonBuying.sessionID.unique()) # 8,740,033 sub groups

t = time.time()
f = open("TimeCompareForItemInNonBuyingSession.txt", "w")
i = 1.
for label, group in gb:
    if (i % 10000 == 0): print str(round(i*100/size,2)) + "%, time cost: " + str(time.time() - t)
    get_item_duration(group)
    i += 1
f.close()
print time.time() - t