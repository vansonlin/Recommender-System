__author__ = 'vanson'

# For whether resulting buying event:
# If a user intensively checked items under a same or similar categories, he/she was likely to buy an item in that session.
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
# # of unique item bought: 19,949


# might result in buying multiple items in one session
# solution file
# session ID, item bought iDs, separated by commas.

############################################################
## this file is for creating the buying session table, 
## 1. each row is for each buying session:
## -> sessionID, bought itemID, # of clicks on that item (in that session), most popular item (not bought), # of clicks, second popular...
############################################################

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import time
import datetime
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

dr = "yoochoose-data/"
# dr = ""
# filename = "yoochoose-clicks.dat"
# filename = "yoochoose-buys.dat"
# filename = "yoochoose-test.dat"

# 2 minutes for loading clicks
t = time.time()
dfClick = pd.read_csv(dr + "yoochoose-clicks.dat", engine='c', header = None, parse_dates = [1],
                      names = ["sessionID", "timestamp", "itemID", "category"])
dfClick.loc[dfClick["category"] == 'S', "category"] = -1 # reindexing all 'S' category to -1
dfClick["category"] = dfClick["category"].astype(int) # withou 'S' category, now the column can be int type.

# list of items, category given categoryID or itemID
categoryGivenItem = dfClick.groupby(["itemID"])["category"].unique() # list of category given one item ID
itemGivenCategory = dfClick.groupby(["category"])["itemID"].unique() # list of items given one category ID
# e.g. categoryGivenItem[214507365] check for item 214507365.

# sessionList = dfClick["sessionID"].unique()
# np.savetxt("sessionList_clicks.txt", sessionList, fmt='%d')
sessionList = np.genfromtxt("sessionList_clicks.txt", dtype='int')
sessionIndex = {}
for i in range(len(sessionList)):
    sessionIndex[sessionList[i]] = i

# itemList = dfClick["itemID"].unique()
# itemList.sort() # make the list in order (small to big)
# np.savetxt("itemList.txt", itemList, fmt='%d')
itemList = np.genfromtxt("itemList.txt", dtype='int')
itemIndex = {}
for i in range(len(itemList)):
    itemIndex[itemList[i]] = i

# categoryList = dfClick["category"].unique()
# categoryList.sort() # category S is represented as -1 here.
# np.savetxt("categoryList.txt", categoryList, fmt='%d')
categoryList = np.genfromtxt("categoryList.txt", dtype='int')
categoryIndex = {}
for i in range(len(categoryList)):
    categoryIndex[categoryList[i]] = i

### read buy dataset
dfBuy = pd.read_csv(dr + "yoochoose-buys.dat", engine='c', header = None, parse_dates = [1],
                    names = ["sessionID", "itemstamp", "itemID", "price", "quantity"])
# # of unique session ID: 509,696, all exist in click data set
# # of unique item ID: 19,949, all exist in click data set
# a buying session may buy more than 1 item.
buyingSessionList = dfBuy["sessionID"].unique()
buyingItemList = dfBuy["itemID"].unique()

print "Loading Done. t = ", time.time() - t

##############################
# 1/5
# TODO: Two tables
# 1. each row is for each buying session:
# -> sessionID, bought itemID, # of clicks on that item (in that session), most popular item (not bought), # of clicks, second popular...
# 2. each row is for each other session (no buying resulted):
# -> sessionID, most popular item(most clicks in that session), # of clicks, second popular item, # of clicks...
def getKey(item): # for sorting a list based on index 1 element
    return item[1]

open("log.txt", "w").close()
f = open("ClickNumTable_buying.txt","w")

# row = []
for i in range(len(buyingSessionList)):
    if (i % 5000 == 0):
        s = str(i) + "\t" + str(round(i*100. / len(buyingSessionList),2)) + "%\t" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        with open("log.txt", "r") as log:
            lines = log.readlines()
        with open("log.txt", "w") as log:
            for line in lines:
                log.write(line)
            log.write("%s" %s)
            log.write("\n")

    session = buyingSessionList[i]

    boughtItems = dfBuy[dfBuy["sessionID"] == session]["itemID"].unique()
    clickOfSession = dfClick[dfClick["sessionID"] == session]
    clickedItems = clickOfSession["itemID"].unique()
    nonBoughtItems = np.setdiff1d(clickedItems, boughtItems)

    otherItemClick = []
    clickSize = clickOfSession.groupby(["itemID"]).size()
    for nonBoughtItem in nonBoughtItems:
        otherItemClick.append([nonBoughtItem, clickSize[nonBoughtItem]])
    # otherItemClick = np.array(otherItemClick)
    if (len(otherItemClick) != 0):
        otherItemClick.sort(key=getKey, reverse = True)

        # otherItemClick = otherItemClick[otherItemClick.argsort(axis=0)[:,1][::-1]].flatten().tolist()

    for boughtItem in boughtItems:
        if (len(otherItemClick) == 0):
            f.write("%d" %session)
            f.write(",%d" %boughtItem)
            f.write(",%d" %(clickSize[boughtItem]+1))
            f.write("\n")
        else:
            f.write("%d" %session)
            f.write(",%d" %boughtItem)
            f.write(",%d" %(clickSize[boughtItem]+1))
            for item in otherItemClick:
                f.write(",%d" %item[0])
                f.write(",%d" %item[1])
            f.write("\n")

with open("log.txt", "r") as log:
    lines = log.readlines()
with open("log.txt", "w") as log:
    for line in lines:
        log.write(line)
    log.write("\nDone. %s" %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    # log.write("%s\n" %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
f.close()


# with open("ClickNumTable_buying.txt","w") as f:
#     for r in row:
#         f.write("%d" %r[0])
#         for element in r[1:]:
#             f.write(",%d" %element)
#         f.write("\n")

# a session may buy more than once on the same item, it is counted as once in this table.

# session = buyingSessionList[8]
# print dfBuy[dfBuy["sessionID"] == session].head(20)
# print dfClick[dfClick["sessionID"] == session].head(50)

# dfClick.head()
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


