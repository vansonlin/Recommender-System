__author__ = 'vanson'
'''
This code set is to create the feature set for all clicks from training dataset
Each session is one line, and contains the following feature set

More feature details can be found in the class Feature_Generator description

The input of the constructor of Feature_Generator class is
a pandas data frame of all the click records in a same session

#########################
number of buying session:    509696
number of all session:      9249729
'''

class Feature_Generator:
    '''
    pandas data frame of a certain session is the Input of the constructor.

    For example, all clicks are in one session

            sessionID                  timestamp     itemID  category
    24         11 2014-04-03 10:44:35.672000  214821275         0
    25         11 2014-04-03 10:45:01.674000  214821275         0
    26         11 2014-04-03 10:45:29.873000  214821371         0
    27         11 2014-04-03 10:46:12.162000  214821371         0
    28         11 2014-04-03 10:46:57.355000  214821371         0
    29         11 2014-04-03 10:53:22.572000  214717089         0
    30         11 2014-04-03 10:53:49.875000  214563337         0
    31         11 2014-04-03 10:55:19.267000  214706462         0
    32         11 2014-04-03 10:55:47.327000  214717436         0
    33         11 2014-04-03 10:56:30.520000  214743335         0
    34         11 2014-04-03 10:57:19.331000  214826837         0
    35         11 2014-04-03 10:57:39.433000  214819762         0

    1) number of clicked items in total: n1

    2) the distribution of clicks on the top 5 most popular items: d1, d2, d3, d4, d5
    for example, in a session, you have 5 clicks on item1, 3 clicks on item2, 3 clicks on item3, 2 clicks on item4 and 2 click on item5, 10 clicks on other 10 items. that means, items 1 - 5 are the most popular items, and the distribution will be 5/(5+3+3+2+2+10), 3/(5+3+3+2+2+10), 3/(5+3+3+2+2+10),2/(5+3+3+2+2+10),2(5+3+3+2+2+10). If there are fewer than 5 items, then you need to pad 0's to the distribution. In other words, the distribution has 5 dimensions always.

    3) the duration (the total time) of the session: s1 (s)

    4) the distribution of time spent on the top 5 most popular items: t1, t2, t3, t4, t5
    similar as in 2), first find the top 5 most popular items (the items that are clicked most), and calculate the total time spent on such items and calculate their distribution as in 2). Pad 0's if necessary. the distribution will have 5 dimensions.

    5) the distribution of time spent on the top 5 most time-consuming items: c1, c2, c3, c4, c5
    first find the top 5 items on which the user spent most of the time in the session, and then calculate the distribution of the spent time. Pad 0's if necessary

    6) the distribution of clicks on the top 5 most time-consuming items: r1, r2, r3, r4, r5
    similar as 5), first find the top 5 most time-consuming items, and calculate the distribution of their clicks

    7) calculate the transition probabilities among the items and find the top 5 largest values from all the probabilities: p1, p2, p3, p4, p5
    for example, if the session looks like this: a->b->a->c->b->a, then calculate the probability of all the transitions a->b, b->a, a->c, c->b (in this case, it is 1/5, 2/5, 1/5, 1/5, 1/5). then find the largest probabilities

    8) total number of clicks: b1

    9) max number of clicks on a single item: max1
    10) min number of clicks on a single item: min1
    11) average number of clicks on an item: mean1
    12) median number of clicks on a single item: median1
    13) max time spent on a single item: maxt1
    14) min time spent on a single item: mint1
    15) average time spent on an item: meant1
    16) median time spent on a single item: mediant1

    for each session, it feature vector is constructed as
    [sessionID, Label: Buy or Not (1/0), n1, d1, d2, d3, d4, d5, s1, t1, t2, t3, t4, t5, c1, c2, c3, c4, c5, r1, r2, r3, r4, r5, p1, p2, p3, p4, p5, b1, max1, min1, mean1, median1, maxt1, mint1, meant1, median1],
    that is, the feature vector will be a concatenation of all the 16 types of features.
    '''
    def __init__(self, buying_session_hash, df):
        self.buying_session_hash = buying_session_hash
        self.df = df

        self.buying = buying_session_hash.has_key(df.sessionID.values[0])
        self.number_clicks = len(df)
        self.duration = float(df.timestamp.values[-1] - df.timestamp.values[0])/pow(10,9) # time duration of the session

        self.clicks_on_item_dict = None # dictionary: {itemID : number of clicks on the item}
        self.item_popular_list = None # the list of itemID in the order of popularity (Decreasing)
        self.__find_item_popular() # calculate the clicks_on_item, item_popular_list values

        self.time_on_item_dict = None # dictionary: {itemID : time spent duration on the item}
        self.item_time_spent_list = None # the list of itemID in the longest time order (Decreasing)
        self.__find_item_time()

        self.transition_count_dict = None # count of itemID transition
        self.transition_key_list = None # transition label in decreasing order
        self.__find_transition_dict()

    def generate_all_feature(self):
        '''
        [sessionID, Label: Buy or Not (1/0), n1, d1, d2, d3, d4, d5, s1, t1, t2, t3, t4, t5, c1, c2, c3, c4, c5, r1, r2, r3, r4, r5, p1, p2, p3, p4, p5, b1, u1, max1, min1, mean1, median1, maxt1, mint1, meant1, median1],

        :return: a list of sessionID, label (Buying or not) and all features
        '''
        feature_vector = [self.df.sessionID.values[0]] # 0
        feature_vector.append(self.get_session_buying()) # 1
        feature_vector.append(self.get_1_number_items()) # 2
        for val in self.get_2_click_distribution_on_popular_items(): # 3-7
            feature_vector.append(val)
        feature_vector.append(self.get_3_duration()) # 8
        for val in self.get_4_time_distribution_on_popular_items(): # 9-13
            feature_vector.append(val)
        for val in self.get_5_time_distribution_on_time_consuming_item(): # 14-18
            feature_vector.append(val)
        for val in self.get_6_click_distribution_on_time_consuming_items(): # 19-23
            feature_vector.append(val)
        for val in self.get_7_transition_distribution(): # 24-28
            feature_vector.append(val)
        feature_vector.append(self.get_8_total_number_clicks()) # 29
        feature_vector.append(self.get_9_max_clicks_on_one_item()) # 30
        feature_vector.append(self.get_10_min_clicks_on_one_item()) # 31
        feature_vector.append(self.get_11_ave_clicks_on_one_item()) # 32
        feature_vector.append(self.get_12_median_clicks_on_one_item()) # 33
        feature_vector.append(self.get_13_max_time_on_one_item()) # 34
        feature_vector.append(self.get_14_min_time_on_one_item()) # 35
        feature_vector.append(self.get_15_ave_time_on_one_item()) # 36
        feature_vector.append(self.get_16_median_time_on_one_item()) # 37

        return feature_vector

    def __find_item_popular(self):
        '''
        private method
        find the popular order of items, and create the number of clicks on item dictionary
        '''

        item_list = self.df.itemID.values
        self.clicks_on_item_dict = {} # attribute
        for i in item_list:
            if self.clicks_on_item_dict.has_key(i):
                self.clicks_on_item_dict[i] += 1
            else:
                self.clicks_on_item_dict[i] = 1

        ## sort the list based on counts
        # 1. create size*2 list
        keys = self.clicks_on_item_dict.keys()
        item_counts = []
        for key in keys:
            item_counts.append([key, self.clicks_on_item_dict[key]])

        # 2. sort the list based on counts
        from operator import itemgetter
        item_counts.sort(key=itemgetter(1), reverse=True)
        self.item_popular_list = [i for i, j in item_counts] # attribute

    def __find_item_time(self):
        itemID_list = self.df.itemID.values
        timestamp_list = self.df.timestamp.values

        self.time_on_item_dict = {} # attributes
        for item in self.df.itemID.unique():
            self.time_on_item_dict[item] = 0.

        for i in range(len(timestamp_list) - 1):
            self.time_on_item_dict[itemID_list[i]] += float(timestamp_list[i + 1] - timestamp_list[i])/pow(10, 9)

        ## sort the list based on time spent
        # 1. create size*2 list
        keys = self.clicks_on_item_dict.keys()
        time_spent = []
        for key in keys:
            time_spent.append([key, self.time_on_item_dict[key]])

        # 2. sort the list based on time spent
        from operator import itemgetter
        time_spent.sort(key=itemgetter(1), reverse=True)

        self.item_time_spent_list = [i for i, j in time_spent] # attribute

    def __find_transition_dict(self):
        '''
        7) calculate the transition probabilities among the items and find the top 5 largest values from all the probabilities: p1, p2, p3, p4, p5
        for example, if the session looks like this: a->b->a->c->b->a, then calculate the probability of all the transitions a->b, b->a, a->c, c->b (in this case, it is 1/5, 2/5, 1/5, 1/5, 1/5). then find the largest probabilities

        create two attributes
        1. self.transition_count_dict
        2. self.transition_key_list

        '''
        self.transition_count_dict = {} # attribute
        item_list = self.df.itemID.values
        for i in range(len(item_list) - 1):
            key = str(item_list[i]) + "_" + str(item_list[i+1])
            if self.transition_count_dict.has_key(key):
                self.transition_count_dict[key] += 1
            else:
                self.transition_count_dict[key] = 1

        ## sort the list based on count
        # 1. create (size-1)*2 list
        keys = self.transition_count_dict.keys()
        count_list = []
        for key in keys:
            count_list.append([key, self.transition_count_dict[key]])

        # 2. sort the list based on second column
        from operator import itemgetter
        count_list.sort(key=itemgetter(1), reverse=True)
        self.transition_key_list = [i for i, j in count_list] # attribute

    def get_session_buying(self):
        '''
        :return: 1/0 if this session result buying or not. (Label of the session)
        '''
        if self.buying:
            return 1 # buy resulted
        else:
            return 0 # non buy

    def get_1_number_items(self):
        '''
        1) number of clicked items in total: n1

        :return: number of items clicked in that session
        '''
        return len(self.item_popular_list)

    def get_2_click_distribution_on_popular_items(self):
        '''
        2)
        The distribution of clicks on the top 5 most popular items: d1, d2, d3, d4, d5

        for example, in a session, you have 5 clicks on item1, 3 clicks on item2, 3 clicks on item3, 2 clicks on item4
        and 2 click on item5, 10 clicks on other 10 items.
        That means, items 1 - 5 are the most popular items, and the distribution will be
        5/(5+3+3+2+2+10), 3/(5+3+3+2+2+10), 3/(5+3+3+2+2+10),2/(5+3+3+2+2+10),2(5+3+3+2+2+10).
        If there are fewer than 5 items, then you need to pad 0's to the distribution.
        In other words, the distribution has 5 dimensions always.

        :return: a list of 5 values.
        '''

        counts = [float(self.clicks_on_item_dict[item])/self.number_clicks for item in self.item_popular_list[:5]]
        if len(counts) < 5:
            counts += [0.]*(5-len(counts))
        return counts

    def get_3_duration(self):
        '''
        3) the duration (the total time) of the session: s1 (s)

        :return: the duration of this session, in second
        '''
        return self.duration

    def get_4_time_distribution_on_popular_items(self):
        '''
        4) the distribution of time spent on the top 5 most popular items: t1, t2, t3, t4, t5
        similar as in 2), first find the top 5 most popular items (the items that are clicked most), and calculate the total time spent on such items and calculate their distribution as in 2). Pad 0's if necessary. the distribution will have 5 dimensions.

        Normalization is based on the total time duration on that session

        :return: a list of 5 (normalized) time duration on top 5 most popular items
        '''
        if self.duration != 0:
            time_spent = [self.time_on_item_dict[i]/self.duration for i in self.item_popular_list[:5]]
            if len(time_spent) < 5:
                time_spent += [0.]*(5-len(time_spent))
            return time_spent
        else:
            return [0.,0.,0.,0.,0.]

    def get_5_time_distribution_on_time_consuming_item(self):
        '''
        5) the distribution of time spent on the top 5 most time-consuming items: c1, c2, c3, c4, c5
        first find the top 5 items on which the user spent most of the time in the session, and then calculate the distribution of the spent time. Pad 0's if necessary

        :return: a list with 5 (normalized) time durations  of top 5 most time consuming items
        '''
        if self.duration != 0:
            time_spent = [self.time_on_item_dict[i]/self.duration for i in self.item_time_spent_list[:5]]
            if len(time_spent) < 5:
                time_spent += [0.]*(5-len(time_spent))
            return time_spent
        else:
            return [0.,0.,0.,0.,0.]

    def get_6_click_distribution_on_time_consuming_items(self):
        '''
        6) the distribution of clicks on the top 5 most time-consuming items: r1, r2, r3, r4, r5
        similar as 5), first find the top 5 most time-consuming items, and calculate the distribution of their clicks

        :return: a list of 5 values.
        '''

        counts = [float(self.clicks_on_item_dict[item])/self.number_clicks for item in self.item_time_spent_list[:5]]
        if len(counts) < 5:
            counts += [0.]*(5-len(counts))
        return counts

    def get_7_transition_distribution(self):
        '''
        7) calculate the transition probabilities among the items and find the top 5 largest values from all the probabilities: p1, p2, p3, p4, p5
        for example, if the session looks like this: a->b->a->c->b->a, then calculate the probability of all the transitions a->b, b->a, a->c, c->b (in this case, it is 1/5, 2/5, 1/5, 1/5, 1/5). then find the largest probabilities

        :return: a list of 5 floating values
        '''
        transition_prob = [float(self.transition_count_dict[key])/(self.number_clicks-1) for key in self.transition_key_list[:5]]
        if len(transition_prob) < 5:
            transition_prob += [0.]*(5-len(transition_prob))
        return transition_prob

    def get_8_total_number_clicks(self):
        '''
        8) total number of clicks: b1

        :return: an int
        '''
        return self.number_clicks

    def get_9_max_clicks_on_one_item(self):
        '''
        9) max number of clicks on a single item: max1
        :return:
        '''
        return self.clicks_on_item_dict[self.item_popular_list[0]]

    def get_10_min_clicks_on_one_item(self):
        '''
        10) min number of clicks on a single item: min1

        :return:
        '''
        return self.clicks_on_item_dict[self.item_popular_list[-1]]

    def get_11_ave_clicks_on_one_item(self):
        '''
        11) average number of clicks on an item: mean1

        :return:
        '''
        return float(self.number_clicks)/len(self.item_popular_list)

    def get_12_median_clicks_on_one_item(self):
        '''
        12) median number of clicks on a single item: median1

        :return:
        '''
        length = len(self.item_popular_list)
        if length % 2 == 0: # even number, median is the ave of n/2, (n/2)+1
            return float(self.clicks_on_item_dict[self.item_popular_list[length/2 - 1]] + self.clicks_on_item_dict[self.item_popular_list[length/2]])/2
        else:
            return float(self.clicks_on_item_dict[self.item_popular_list[length/2]])

    def get_13_max_time_on_one_item(self):
        '''
        13) max time spent on a single item: maxt1

        :return:
        '''
        return self.time_on_item_dict[self.item_time_spent_list[0]]

    def get_14_min_time_on_one_item(self):
        '''
        14) min time spent on a single item: mint1

        :return:
        '''
        return self.time_on_item_dict[self.item_time_spent_list[-1]]

    def get_15_ave_time_on_one_item(self):
        '''
        15) average time spent on an item: meant1

        :return:
        '''
        return self.duration/len(self.item_popular_list)

    def get_16_median_time_on_one_item(self):
        '''
        16) median time spent on a single item: mediant1

        :return:
        '''
        length = len(self.item_time_spent_list)
        if length % 2 == 0: # even number, median is the ave of n/2, (n/2)+1
            return float(self.time_on_item_dict[self.item_time_spent_list[length/2 - 1]] + self.time_on_item_dict[self.item_time_spent_list[length/2]])
        else:
            return float(self.time_on_item_dict[self.item_time_spent_list[length/2]])

import pandas as pd
import numpy as np

dr = "yoochoose-data/"
dfClick = pd.read_csv(dr + "yoochoose-clicks.dat", engine='c', header=None, parse_dates=[1],
                      names=["sessionID", "timestamp", "itemID", "category"])
gbClick = dfClick.groupby("sessionID")

# create session ID hash table for fast exam existence
buying_session_hash = {}
f = open(dr + "sessionList_buying.txt", "r")
line = f.readline()
while(len(line) > 1):
    line = int(line[:-1])
    if not buying_session_hash.has_key(line):
        buying_session_hash[line] = True
    line = f.readline()
f.close()

# Generate feature vectors and write to output file
f = open("feature_set.txt", "w")
# append description of the feature generator first
f.write('''1) number of clicked items in total: n1

2) the distribution of clicks on the top 5 most popular items: d1, d2, d3, d4, d5
for example, in a session, you have 5 clicks on item1, 3 clicks on item2, 3 clicks on item3, 2 clicks on item4 and 2 click on item5, 10 clicks on other 10 items. that means, items 1 - 5 are the most popular items, and the distribution will be 5/(5+3+3+2+2+10), 3/(5+3+3+2+2+10), 3/(5+3+3+2+2+10),2/(5+3+3+2+2+10),2(5+3+3+2+2+10). If there are fewer than 5 items, then you need to pad 0's to the distribution. In other words, the distribution has 5 dimensions always.

3) the duration (the total time) of the session: s1 (s)

4) the distribution of time spent on the top 5 most popular items: t1, t2, t3, t4, t5
similar as in 2), first find the top 5 most popular items (the items that are clicked most), and calculate the total time spent on such items and calculate their distribution as in 2). Pad 0's if necessary. the distribution will have 5 dimensions.

5) the distribution of time spent on the top 5 most time-consuming items: c1, c2, c3, c4, c5
first find the top 5 items on which the user spent most of the time in the session, and then calculate the distribution of the spent time. Pad 0's if necessary

6) the distribution of clicks on the top 5 most time-consuming items: r1, r2, r3, r4, r5
similar as 5), first find the top 5 most time-consuming items, and calculate the distribution of their clicks

7) calculate the transition probabilities among the items and find the top 5 largest values from all the probabilities: p1, p2, p3, p4, p5
for example, if the session looks like this: a->b->a->c->b->a, then calculate the probability of all the transitions a->b, b->a, a->c, c->b (in this case, it is 1/5, 2/5, 1/5, 1/5, 1/5). then find the largest probabilities

8) total number of clicks: b1

9) max number of clicks on a single item: max1
10) min number of clicks on a single item: min1
11) average number of clicks on an item: mean1
12) median number of clicks on a single item: median1
13) max time spent on a single item: maxt1
14) min time spent on a single item: mint1
15) average time spent on an item: meant1
16) median time spent on a single item: mediant1

for each session, it feature vector is constructed as
[sessionID, Label: Buy or Not (1/0), n1, d1, d2, d3, d4, d5, s1, t1, t2, t3, t4, t5, c1, c2, c3, c4, c5, r1, r2, r3, r4, r5, p1, p2, p3, p4, p5, b1, max1, min1, mean1, median1, maxt1, mint1, meant1, median1]
################################## skip 33 lines
''')
import time

t = time.time()
n_total_session = len(dfClick.sessionID.unique())
current_n_session = 0
print "number of total sessions:", n_total_session

for sessionID, df in gbClick:
    current_n_session += 1
    if (current_n_session % 50000 == 0):
        print str(round(current_n_session*100./n_total_session, 2)) + "%, time spent:", time.time() - t
    feature_generator = Feature_Generator(buying_session_hash, df)
    feature_vector = feature_generator.generate_all_feature()
    f.write(str(feature_vector[0]))
    for i in feature_vector[1:]:
        f.write("," + str(i))
    f.write("\n")
f.close()


## create the small one (first 50,000 lines)
t = time.time()
f_small = open("feature_set_small.txt", "w")
f_big = open("feature_set.txt", "r")
for i in range(50000):
    f_small.write(f_big.readline())
f_small.close()
f_big.close()
print time.time() - t



# selected the target session ID
# construct feature generator object
# a = Feature_Generator(buying_session_hash, gbClick.get_group(83))

# f = open("feature_set.txt", "w") # feature set output file

