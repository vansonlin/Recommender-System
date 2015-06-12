__author__ = 'vanson'

'''
The code produce Big, and Small testing sets. (Full Sessions)


Test Set:
P: Records in complete buying sessions -> 300k sessions		ItemFeatures_BuySessions_300k_Session.txt
N: Records in complete no-buying sessions -> 300k sessions 	ItemFeatures_Non-BuySessions_300k_Session.txt

P: Records in complete buying sessions -> 20k sessions		ItemFeatures_BuySessions_20k_Session.txt
N: Records in complete no-buying sessions -> 20k sessions	ItemFeatures_Non-BuySessions_20k_Session.txt


The 300k datasets are used to generate training set.

Note:
for non-buying records from non-buying sessions, the labels are 0
	+1: buying from buying sessions
	 0: non-buying from non-buying sessions
	-1: non-buying from buying sessions

Change the get_label method when switching between buying/non-buying sessions
'''


'''

*Gradient boosting tree
features on item:
Local:
	Clicks on item
	Time on item (with estimation on the last click)
	Percentage time on item (normalization on total time)
	percentage click on item (normalization on total click)
	Has returned click (0/1, not discrete)
	Has returned click (0/1, continuous)
	3 locations (front, middle, late)
	Integrated location (percentage)
	If item bought by other (0/1)
	N bought before
	Clicked by N other buying session
	Value in Random Walk (matrix)

## stats:
1. with estimate time on the last click,
	a. if total time was normalized as  2*total/(number of unique item)
		Bought Item occupies for 65.25% of session time in average, std = 0.55
		Non-Bought Item occupies for 40.6% of session time in average, std = 0.476
	b. if total time was not normalized
		Each Bought Item occupies for 24.4% of session time in average, std = 0.22
		Each Non-Bought Item occupies for 12% of session time in average, std = 0.14

2. discrete returned click: [308171, 1730386] (bought item : non-bought item)
3. continuous returned click: [270967, 1767590] (bought item : non-bought item)

Random Walk:
	If last clicked item was clicked only once, then there is a whole row being zero. Cannot produce eigenvector.

	Solution:
	 a. only focus on sessions whose last click is a returned click
	 b. fill the zero row with equal probabilities.
'''

import numpy as np
import time
import operator
import random


class Feature_Generator:
	def __init__(self, sessionID, clicks, hash_clicks_on_item):
		self.sessionID = sessionID
		self.clicks = clicks.split(";")
		self.hash_clicks_on_item = hash_clicks_on_item

		self.item_flow = [] # int type
		self.time_spent = [] # int type
		self.item_bought = set() # set
		self.item_non_bought = set()
		self.hash_time_on_item = {}
		self.hash_indices_of_click_on_item = {}
		self.total_time = 0. # float type
		self.analysis() # construct all information

		self.hash_random_walk_value_on_item = None

		# main code

		# self.printAll()
		# self.get_all_features_and_write()

	def printAll(self):
		print
		print self.sessionID
		for click in self.clicks:
			print "\t".join(click)
		print "item flow:", self.item_flow
		print "indices of click", self.hash_indices_of_click_on_item
		print "time spent:", self.time_spent
		print "item bought:", self.item_bought
		print "item non bought:", self.item_non_bought
		print "aggregated time on item:", self.hash_time_on_item
		print "total time:", self.total_time

	def analysis(self):
		old_time = 0
		if self.sessionID not in hash_bSession_items:
			self.item_bought = set()
		else:
			self.item_bought = hash_bSession_items[self.sessionID]

		for i in range(len(self.clicks)):
			click = self.clicks[i].split(",")
			self.clicks[i] = click

			if old_time != 0:
				self.time_spent.append((np.datetime64(click[0]) - old_time).item().seconds)
			old_time = np.datetime64(click[0])

			item = click[1]
			self.item_flow.append(item)

			if item not in self.item_bought:
				self.item_non_bought.add(item)

			if item not in self.hash_indices_of_click_on_item:
				self.hash_indices_of_click_on_item[item] = [i]
			else:
				self.hash_indices_of_click_on_item[item].append(i)

		if len(self.time_spent) == 0: # if only one click, no time available
			self.time_spent = [90.]
		else:
			self.time_spent.append(int(np.mean(self.time_spent))) # estimate on the last click

		# build hash- time on item
		for i in range(len(self.item_flow)):
			if self.item_flow[i] not in self.hash_time_on_item:
				self.hash_time_on_item[self.item_flow[i]] = self.time_spent[i]
			else:
				self.hash_time_on_item[self.item_flow[i]] += self.time_spent[i]

		self.total_time = sum(self.time_spent)*1. # float type

	def build_random_walk_hash(self):
		hash_item_indices = {} # 'ItemID' -> index
		item_list = list(self.hash_time_on_item)
		for i in range(len(item_list)):
			hash_item_indices[item_list[i]] = i

		# construct matrix
		matrix = np.array([[0.]*len(item_list)]*len(item_list))
		for i in range(1, len(self.item_flow)):
			start = self.item_flow[i - 1]
			destination = self.item_flow[i]
			matrix[hash_item_indices[start], hash_item_indices[destination]] += 1

		# normalization
		s = matrix.sum(axis=1)
		for i in range(len(s)):
			if s[i] != 0:
				matrix[i] /= s[i]
		v = np.linalg.eig(matrix.T)[1][:,0] # eigenvector

		# build hash table for random work
		hash_random_walk_value_on_item = {}
		for i in hash_item_indices:
			hash_random_walk_value_on_item[i] = v[hash_item_indices[i]].real # only focus on real number
		self.hash_random_walk_value_on_item = hash_random_walk_value_on_item

	def get_all_features_and_write(self, sample=False):
		## randomly select some items

		if sample:
			# 0. decide how many to choose in buy and non-buy
			N = min(len(self.item_bought), len(self.item_non_bought))

			items = []
			items.extend(random.sample(list(self.item_bought), N))
			items.extend(random.sample(list(self.item_non_bought), N))
		else:
			items = list(self.hash_time_on_item)

		# sessionID, itemID, features
		sep = ","
		for item in items:
			f.write(self.sessionID + sep + item + sep + self.get_label(item))
			f.write(sep + self.get_feature_clicks_on_item(item))
			f.write(sep + self.get_feature_time_on_item(item))
			f.write(sep + self.get_feature_percentage_time_on_item(item))
			f.write(sep + self.get_feature_percentage_click_on_item(item))
			f.write(sep + self.get_feature_has_returned_click_discrete(item))
			f.write(sep + self.get_feature_has_returned_click_continuous(item))

			front, middle, rear = self.get_feature_locations(item)
			f.write(sep + front)
			f.write(sep + middle)
			f.write(sep + rear)

			f.write(sep + self.get_feature_integrated_location(item))
			f.write(sep + self.get_feature_if_bought_by_other(item))
			f.write(sep + self.get_feature_N_bought_before(item))
			f.write(sep + self.get_feature_Clicked_by_N_other_buying_session(item))
			f.write(sep + self.get_feature_Random_Walk(item))

			features = hash_other_features_on_item[item] # 6+7
			f.write(sep + sep.join(features))

			f.write("\n")

	def get_label(self, item): # be sure to change the labels
		if item in self.item_bought:
			return '+1'
		return '-1'

	def get_feature_clicks_on_item(self, item):
		# Clicks on item
		return str(self.hash_clicks_on_item[item])

	def get_feature_time_on_item(self, item):
		# Time on item (with estimation on the last click)
		return str(self.hash_time_on_item[item])

	def get_feature_percentage_time_on_item(self, item):
		# Percentage time on item (normalization on total time)
		if self.total_time == 0:
			return '0'
		return str(self.hash_time_on_item[item]/(self.total_time/len(self.hash_time_on_item)))

	def get_feature_percentage_click_on_item(self, item):
		# percentage click on item (normalization on total click)
		return str(self.hash_clicks_on_item[item]*1./len(self.clicks))

	def get_feature_has_returned_click_discrete(self, item):
		# Has returned click (0/1, discrete)
		first = False
		second = False
		third = False
		for i in self.item_flow:
			if first == True and i != item:
				second = True
			elif first == False and i == item:
				first = True
			elif second == True and i == item:
				third = True

		if third == True:
			return '1'
		return '0'

	def get_feature_has_returned_click_continuous(self, item):
		# Has returned click (0/1, continuous)
		for i in range(1, len(self.item_flow)):
			if  self.item_flow[i] == item and self.item_flow[i-1] == item:
				return '1'
		return '0'

	def get_feature_locations(self, item):
		# 3 locations (front, middle, late)
		length = (len(self.clicks) - 1)*1.
		if length == 0:
			return ['1', '1', '1']

		front = '0'
		middle = '0'
		rear = '0'
		for i in self.hash_indices_of_click_on_item[item]:
			score = i/length
			if score <= 0.33:
				front = '1'
			elif score >= 0.67:
				rear = '1'
			else:
				middle = '1'
		return [front, middle, rear]

	def get_feature_integrated_location(self, item):
		# Integrated location (percentage)
		if len(self.clicks) == 1:
			return '1'
		scores = []
		for i in self.hash_indices_of_click_on_item[item]:
			scores.append(i*1./(len(self.clicks) - 1))
		return str(np.mean(scores))

	def get_feature_if_bought_by_other(self, item):
		# If item bought by others (0/1)
		if item in hash_item_bought_count:
			return '1'
		return '0'

	def get_feature_N_bought_before(self, item):
		# If item bought by other (0/1)
		if item in hash_item_bought_count:
			return str(hash_item_bought_count[item])
		return '0'

	def get_feature_Clicked_by_N_other_buying_session(self, item):
		if item not in hash_count_buy_session_view_on_item:
			return '0'
		return str(hash_count_buy_session_view_on_item[item])

	def get_feature_Random_Walk(self, item):
		if self.hash_random_walk_value_on_item == None:
			self.build_random_walk_hash()
			return str(self.hash_random_walk_value_on_item[item])
		else:
			return str(self.hash_random_walk_value_on_item[item])


def get_hash_bSession_items():
	hash_bSession_items = {}
	f = open("yoochoose-data/session_bought_items.txt", "r")
	for line in f:
		line = line[:-1].split(";")
		hash_bSession_items[line[0]] = set(line[1].split(","))
	f.close()
	return hash_bSession_items


def get_hash_item_bought_count():
	hash_item_bought_count = {}
	f = open("yoochoose-data/Rec_BoughtItemCount2.txt", "r")
	for line in f:
		line = line[:-1].split(",")
		hash_item_bought_count[line[0]] = int(line[1])
	f.close()
	return hash_item_bought_count


def get_hash_clicks_on_item(clicks): #[itemID] -> n of clicks
	hash_clicks_on_item = {}
	for click in clicks:
		click = click.split(",")
		if click[1] in hash_clicks_on_item:
			hash_clicks_on_item[click[1]] += 1
		else:
			hash_clicks_on_item[click[1]] = 1
	return hash_clicks_on_item


def get_hash_count_buy_session_view_on_item():
	hash_count_buy_session_view_on_item = {}
	f = open("yoochoose-data/CountOfClickOnItemInBuying.txt", "r")
	for line in f:
		item, count = line[:-1].split(" ")
		hash_count_buy_session_view_on_item[item] = int(count)
	f.close()
	return hash_count_buy_session_view_on_item


def get_hash_other_features_on_item():
	hash_other_features_on_item = {}
	dr = "samples/itemFeatures/"
	f_map = open(dr + "itemID_idx_map_all.txt", "r")
	f_feature7 = open(dr + "Vt_sqrtS_allUI_7.txt", "r")
	f_feature6 = open(dr + "Vt_sqrtS_item_cos_all_6.txt", "r")
	for line in f_map:
		line = line[:-1].split(" ")
		itemID = line[0]
		line6 = f_feature6.readline()[:-1].split(" ")
		line7 = f_feature7.readline()[:-1].split(" ")

		features = []
		features.extend(line6)
		features.extend(line7)
		hash_other_features_on_item[itemID] = features
	return hash_other_features_on_item



####################
## Initialization ##
####################

hash_bSession_items = get_hash_bSession_items()
hash_item_bought_count = get_hash_item_bought_count()
hash_count_buy_session_view_on_item = get_hash_count_buy_session_view_on_item()
hash_other_features_on_item = get_hash_other_features_on_item()

###########################################################
## Produce big/small full session set for non-buying (0) ##
###########################################################

def is_target_Test_non_buying(sessionID, clicks):
	clicks = clicks.split(";")
	hash_clicks_on_item = get_hash_clicks_on_item(clicks)
	return hash_clicks_on_item, random.random() < 0.00229 # 0.034325: 300k non-buying sessions. 0.002288: 20k non-buying sessions (20/8740)


def scan_dataset_non_buying(target_test):
	c = 0
	f = open("yoochoose-data/yooAll.txt", "r")
	for line in f:
		if c >= 20000:
			return
		line = line[:-1].split(" ")
		sessionID = line[0]
		if len(line) == 2: # is non-buying session
			hash_clicks_on_item, valid = target_test(sessionID, line[1])
			if valid and sessionID:
				c += 1
				feature_generator = Feature_Generator(sessionID, line[1], hash_clicks_on_item)
				feature_generator.get_all_features_and_write(sample=False)
	f.close()

## For not repeat sessionIDs
# s1 = set()
# f = open("ItemFeatures/ItemFeatures_Non-BuySessions_20k_Session1.txt", "r")
# for line in f:
# 	s1.add(line.split(",")[0])
# f.close()

t = time.time()
f = open("ItemFeatures/ItemFeatures_Non-BuySessions_20k_Session3.txt", "w")
scan_dataset_non_buying(is_target_Test_non_buying)
f.close()
print "Done, Time:", time.time() - t

##########################################################
## Produce big/small full session set for buying (-1,1) ##
##########################################################

def is_target_Test_buying(sessionID, clicks):
	clicks = clicks.split(";")
	hash_clicks_on_item = get_hash_clicks_on_item(clicks)
	return hash_clicks_on_item, random.random() < 0.05 # 0.58858: 300k buying sessions. 0.03924: 20k buying session


def scan_dataset_buying(target_test):
	c = 0
	f = open("yoochoose-data/yooAll.txt", "r")
	for line in f:
		if c >= 20000:
			return
		line = line[:-1].split(" ")
		sessionID = line[0]
		if len(line) == 3: # is buying session
			hash_clicks_on_item, valid = target_test(sessionID, line[1])
			if valid:
				c += 1
				feature_generator = Feature_Generator(sessionID, line[1], hash_clicks_on_item)
				feature_generator.get_all_features_and_write(sample=False)
	f.close()


# s1 = set()
# f = open("ItemFeatures/ItemFeatures_BuySessions_20k_Session1.txt", "r")
# for line in f:
# 	s1.add(line.split(",")[0])
# f.close()

t = time.time()
f = open("ItemFeatures/ItemFeatures_BuySessions_20k_Session3.txt", "w")
scan_dataset_buying(is_target_Test_buying)
f.close()
print "Done, Time:", time.time() - t

#####################################################
# Simple examine
l = 0
s = set()
f = open("ItemFeatures/ItemFeatures_BuySessions_20k_Session.txt", "r")
for line in f:
	s.add(line.split(",")[0])
	l+=1
f.close()
print len(s), l
