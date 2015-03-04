__author__ = 'vanson'

import pandas as pd
import numpy as np
import time

# Create AllClicksInNoBuyingSession.txt
dr = "yoochoose-data/"

t = time.time()
# crete AllClicksInNoBuyingSession.txt from Clicks dataframe
# dr = ""
dfClick = pd.read_csv(dr + "yoochoose-clicks.dat", engine='c', header=None, parse_dates=[1],
                      names=["sessionID", "timestamp", "itemID", "category"])
# dfClick = dfClick.drop(dfClick.columns[3], 1)  # drop category. sessionID & timestamp, itemID remain
sessionList_noBuying = np.genfromtxt(dr + "sessionList_noBuying.txt", dtype='int')

sessionList_noBuying_hash = {}
for session in sessionList_noBuying:
    sessionList_noBuying_hash[session] = True

dfNonBuying = dfClick[map(sessionList_noBuying_hash.has_key,dfClick["sessionID"].values)]
dfNonBuying = dfNonBuying.sort(["sessionID", "timestamp"])
dfNonBuying.reset_index(inplace=True, drop=True)
dfNonBuying.to_csv("AllClicksInNoBuyingSession.txt")
print time.time() - t
