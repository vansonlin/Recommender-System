__author__ = 'vanson'
import pandas as pd
import numpy as np
import time

'''
Construct AllClicksInBuyingSession.txt
'''
dr = "yoochoose-data/"
# dr = ""
dfClick = pd.read_csv(dr + "yoochoose-clicks.dat", engine='c', header=None, parse_dates=[1],
                      names=["sessionID", "timestamp", "itemID", "category"])
dfClick = dfClick.drop(dfClick.columns[3], 1)  # drop category. sessionID & timestamp, itemID remain
sessionList = np.genfromtxt("yoochoose-data/" + "sessionList_clicks.txt", dtype='int')
# sessionList = np.genfromtxt("sessionList.txt", dtype='int')

dfBuy = pd.read_csv(dr + "yoochoose-buys.dat", engine='c', header=None, parse_dates=[1],
                    names=["sessionID", "timestamp", "itemID", "price", "quantity"])
# # of unique session ID: 509,696, all exist in click data set
# # of unique item ID: 19,949, all exist in click data set
# a buying session may buy more than 1 item.
dfBuy = dfBuy.drop(dfBuy.columns[[3, 4]], 1)  # drop price, quantity. sessionID, timestamp, itemID remain

sessionList_buying = np.genfromtxt(dr + "sessionList_buying.txt", dtype=int)

# fast extract indices of a certain sessionID (use hash/dictionary) in dfBuy
buyingSessionIndexInDFBuy = {}
a = dfBuy.sessionID.values
for i in range(len(a)):
    sessionID = a[i]
    if buyingSessionIndexInDFBuy.has_key(sessionID):
        buyingSessionIndexInDFBuy[sessionID].append(i)
    else:
        buyingSessionIndexInDFBuy[sessionID] = [i]

# keep the indices of click record only if the session resulted buying
indices_buying_session_in_clicks = []
a = dfClick.sessionID.values
for i in range(len(a)):
    if (buyingSessionIndexInDFBuy.has_key(a[i])):
        indices_buying_session_in_clicks.append(i)

# combine all clicks in the buying session with buying records, and sort it with sessionID, timestamp and reindex
dfCombine = dfBuy.append(dfClick.iloc[indices_buying_session_in_clicks])
dfCombine = dfCombine.sort(["sessionID", "timestamp"])
dfCombine.reset_index(inplace=True, drop=True) # reset index
dfCombine.to_csv("AllClicksInBuyingSession.txt")