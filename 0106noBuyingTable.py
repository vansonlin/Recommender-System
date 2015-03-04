__author__ = 'vanson'

# For whether resulting buying event:
# If a user intensively checked items under a same or similar categories, he/she was likely to buy an item in that session.
#
#
# If buying, which item:
# 1. The main factor to decide an item might be price, or review. But in this dataset there is no way to extract the review information.
# 2. The most reviewed item(over all session) is more likely to be bought.

# click file
# Session ID, timestamp, item ID, category
# 33,003,944 clicks (rows)
# # of clicks in one session: 3.567 clicks averagely, max # clicks is 200, min is 1
# # of sessions: 9,249,729
# # of unique items: 52,739
# # of unique categories: 339

# buying file
# session ID, timestamp, item ID, price, quantity

# might result in buying multiple items in one session
# solution file
# session ID, item bought iDs, separated by commas.

############################################################
## this file is for creating the nonBuying session table,
## 2. each row is for each other session (no buying resulted):
## -> sessionID, most popular item(most clicks in that session), # of clicks, second popular item, # of clicks...
############################################################

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import time
import datetime
# ts = time.time()
# st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# dr = "yoochoose-data/"
dr = ""
# filename = "yoochoose-clicks.dat"
# filename = "yoochoose-buys.dat"
# filename = "yoochoose-test.dat"

# 2 minutes for loading clicks
t = time.time()
dfClick = pd.read_csv(dr + "yoochoose-clicks.dat", engine='c', header = None, parse_dates = [1],
                      names = ["sessionID", "timestamp", "itemID", "category"])
# dfClick.loc[dfClick["category"] == 'S', "category"] = -1 # reindexing all 'S' category to -1
# dfClick["category"] = dfClick["category"].astype(int) # withou 'S' category, now the column can be int type.
dfClick = dfClick.drop(dfClick.columns[[1,3]], 1)

# list of items, category given categoryID or itemID
# categoryGivenItem = dfClick.groupby(["itemID"])["category"].unique() # list of category given one item ID
# itemGivenCategory = dfClick.groupby(["category"])["itemID"].unique() # list of items given one category ID
# e.g. categoryGivenItem[214507365] check for item 214507365.

# sessionList = dfClick["sessionID"].unique()
# np.savetxt("sessionList_clicks.txt", sessionList, fmt='%d')
sessionList = np.genfromtxt("sessionList_clicks.txt", dtype='int')
# sessionIndex = {}
# for i in range(len(sessionList)):
#     sessionIndex[sessionList[i]] = i

# itemList = dfClick["itemID"].unique()
# itemList.sort() # make the list in order (small to big)
# np.savetxt("itemList.txt", itemList, fmt='%d')
# itemList = np.genfromtxt("itemList.txt", dtype='int')
# itemIndex = {}
# for i in range(len(itemList)):
#     itemIndex[itemList[i]] = i

# categoryList = dfClick["category"].unique()
# categoryList.sort() # category S is represented as -1 here.
# np.savetxt("categoryList.txt", categoryList, fmt='%d')
# categoryList = np.genfromtxt("categoryList.txt", dtype='int')
# categoryIndex = {}
# for i in range(len(categoryList)):
#     categoryIndex[categoryList[i]] = i

### read buy dataset
dfBuy = pd.read_csv(dr + "yoochoose-buys.dat", engine='c', header = None, parse_dates = [1],
                    names = ["sessionID", "itemstamp", "itemID", "price", "quantity"])
# # of unique session ID: 509,696, all exist in click data set
# # of unique item ID: 19,949, all exist in click data set
# a buying session may buy more than 1 item.
buyingSessionList = dfBuy["sessionID"].unique()
# buyingItemList = dfBuy["itemID"].unique()
noBuyingSessionList = np.setdiff1d(sessionList, buyingSessionList)

buyingSessionHash = {}
for i in buyingSessionList:
    buyingSessionHash[i] = 0

noBuyingSessionIndex = {}
a = dfClick.sessionID.values
for i in range(len(dfClick.sessionID.values)):
    # if i % 100000 == 0: print i
    sessionID = a[i]
    if not (buyingSessionHash.has_key(sessionID)):
        if (noBuyingSessionIndex.has_key(sessionID)):
            noBuyingSessionIndex[sessionID].append(i)
        else:
            noBuyingSessionIndex[sessionID] = [i]

del dfBuy, buyingSessionList, sessionList, buyingSessionHash, a
print "Loading Done. t = ", time.time() - t

############################################################
# 1/5
# TODO: Two tables
# 1. each row is for each buying session:
# -> sessionID, bought itemID, # of clicks on that item (in that session), most popular item (not bought), # of clicks, second popular...
# 2. each row is for each other session (no buying resulted):
# -> sessionID, most popular item(most clicks in that session), # of clicks, second popular item, # of clicks...

def getKey(item): # for sorting a list based on index 1 element
    return item[1]
def writeLog(i):
    s = str(i) + "\t" + str(round(i*100. / lenOfnoBuying,2)) + "%\t" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    with open("logForNoBuy.txt", "r") as log:
        lines = log.readlines()
    with open("logForNoBuy.txt", "w") as log:
        for line in lines:
            log.write(line)
        log.write("%s" %s)
        log.write("\n")

open("logForNoBuy.txt", "w").close()
f = open("ClickNumTable_noBuying.txt","w")
lenOfnoBuying = len(noBuyingSessionList)

for i in range(len(noBuyingSessionList)):
    if (i % 500000 == 0):
        writeLog(i)
        # print i

    session = noBuyingSessionList[i]
    # clickOfSession = dfClick[dfClick["sessionID"] == session]
    # clickedItems = clickOfSession["itemID"].unique()

    # ItemClick = []
    # clickSize = clickOfSession.groupby(["itemID"]).size()
    # clickSize = dfClick[dfClick["sessionID"] == session].groupby(["itemID"]).size()
    clickSize = dfClick.iloc[noBuyingSessionIndex[session]].groupby(["itemID"]).size()
    clickSize.sort(ascending=False)
    count = clickSize.values
    index = clickSize.index
    f.write("%d" %session)
    for j in range(len(count)):
        f.write(",%d" %index[j])
        f.write(",%d" %count[j])
    f.write("\n")

with open("logForNoBuy.txt", "r") as log:
    lines = log.readlines()
with open("logForNoBuy.txt", "w") as log:
    for line in lines:
        log.write(line)
    log.write("\nDone. %s" %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    # log.write("%s\n" %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
f.close()

# print time.time() - t

# a = dfClick.groupby(["sessionID", "itemID"]).size()
# a[a["sessionID"] == 11562149]


# t = time.time()
# # dfClick.ix[[0,1,2,3]]
# dfClick.iloc[[0,1,2,3]]
# print time.time() - t

# a session may buy more than once on the same item, it is counted as once in this table.
#

# session = noBuyingSessionList[6]
# # print dfBuy[dfBuy["sessionID"] == session].head(20)
# print dfClick[dfClick["sessionID"] == session].head(50)

# dfClick.head(30)
# dfClick.tail()
# dfClick.info()

################################################

################################################
# 1/5
# TODO: item-item matrix (element represents the number of times when item i was clicks right after item j)
# save in CSR format

################################################
# TODO: load with panda data frame, 3 dataframes: clicks, session, items
# TODO: time spent in each session, relation to # of clicks
