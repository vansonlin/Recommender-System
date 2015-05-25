__author__ = 'vanson'
'''
Test two recommendation methods (blog method, most click items).
Test on buying session only, use the official Evaluation.

1. Calculate the ratio based on the overall buying session.
	a. N unique items are bought per click. std: 0.2563
	b. N of items bought per item clicked. std: 0.3036

2. Test Recommender Methods
'''

###############################################
## Find the Top X ratio for recommended Item ##
###############################################
import time, numpy as np
import matplotlib.pyplot as plt
import operator

def scan_dataset(filepath, process_records):
	length = len(open(filepath, "r").readlines())
	t = time.time()
	records = []
	sessionID_old = open(filepath, "r").readline().split(",")[0]  # str type
	count = 0
	f = open(filepath, "r")
	for line in f:
		count += 1
		line = line[:-1].split(",")
		sessionID = line[0]  # str type
		if sessionID == sessionID_old:  # same session
			records.append(line)
		else:  # new session
			if (count % 100000 == 0):
				print "Session", str(sessionID) + ":", str(round(count*100./length, 2))+"%", time.ctime()
			process_records(records)
			records = [line]  		# new session
			sessionID_old = line[0]
	process_records(records) 	# last session
	f.close()
	print "Done", time.time() - t


## 0. Scan buying dataset

def process_session_buy(records):
	'''
	:param records: a list of list of buying record in str type
	:return: no return. but extend the hash table -> sessionID: set([bought itemID 1, bought itemID 2, ...])
	'''
	# items = set()
	items = set()
	for record in records:
		items.add(record[2])
	hash_bSession_bought_item_list[records[0][0]] = items

hash_bSession_bought_item_list = {}
print "Start processing bought item hash table..."
scan_dataset("yoochoose-data/" + "yoochoose-buys.dat", process_session_buy)

# ====
# 1a. N unique items are bought per click in the length of the session. (length = number of clicks)

def process_session_click_1a(records):
	if records[0][0] in hash_bSession_bought_item_list:
		ratio = len(hash_bSession_bought_item_list[records[0][0]])*1./len(records)
		if len(records) not in hash_ratio_1a:
			hash_ratio_1a[len(records)] = [ratio]
		else:
			hash_ratio_1a[len(records)].append(ratio)

print "Start processing..."
hash_ratio_1a = {} # ratio varies on length of session
scan_dataset("yoochoose-data/" + "yoochoose-clicks.dat", process_session_click_1a)

list_ratio_1a = [np.array(hash_ratio_1a[i]).mean() for i in hash_ratio_1a]

plt.plot(range(1,len(list_ratio_1a)+1), list_ratio_1a)
plt.title("Ratio of Items to be Recommended to Length of Session")
plt.ylabel("Ratio")
plt.xlabel("Length of Session. (Number of Clicks)")
plt.show()


# =====
# 1b. N unique items are bought per item clicked.

def process_session_click_1b(records):
	if records[0][0] in hash_bSession_bought_item_list:
		item_set = set()
		for record in records:
			item_set.add(record[2])
		ratio = len(hash_bSession_bought_item_list[records[0][0]])*1./len(item_set)
		if len(item_set) not in hash_ratio_1b:
			hash_ratio_1b[len(item_set)] = [ratio]
		else:
			hash_ratio_1b[len(item_set)].append(ratio)

hash_ratio_1b = {}
print "Start processing..."
scan_dataset("yoochoose-data/" + "yoochoose-clicks.dat", process_session_click_1b)

list_ratio_1b = [np.array(hash_ratio_1b[i]).mean() for i in hash_ratio_1b]

plt.plot(range(1,len(list_ratio_1b)+1), list_ratio_1b)
plt.title("Ratio of Items to be Recommended to Length of Session")
plt.ylabel("Ratio")
plt.xlabel("Length of Session. (Number of Items Clicked)")
plt.show()


# =====
# 1c. N unique items are bought per second spent on session (excluding buying click)
# todo: build it


#############################
## Test Recommender Method ##
#############################
def jccard(true_set, predicted_set):
	return len(true_set.intersection(predicted_set))*1./len(true_set.union(predicted_set))

# ====
# Blog Method

class Blog_Method():
	def __init__(self, NBought=10, NClick=2):
		self.NBought = NBought # inclusive
		self.NClick = NClick # inclusive
		self.potential_buying_items = self.build_potential_buying_items("yoochoose-data/BoughtItemCount.txt") # set

	def build_potential_buying_items(self, filepath):
		f = open(filepath, "r")
		s = set()
		for line in f:
			line = line[:-1].split(",")
			if int(line[1]) >= self.NBought:
				s.add(int(line[0]))
		return s

	def make_recommendations(self, records):
		hash_clicks_on_item = {}
		for record in records:
			item = record[2]
			if item not in hash_clicks_on_item:
				hash_clicks_on_item[item] = 1
			else:
				hash_clicks_on_item[item] += 1

		recommendations = set([i for i in hash_clicks_on_item if hash_clicks_on_item[i] >= self.NClick])
		return recommendations

def process_session_recommender_blog(records):
	if records[0][0] in hash_bSession_bought_item_list:
		recommendations = recommender_blog.make_recommendations(records)
		list_score_BlogMethod.append(jccard(hash_bSession_bought_item_list[records[0][0]], recommendations))
		# print "Session", records[0][0], "|recommendations:", recommendations, "|True Items:", hash_bSession_bought_item_list[records[0][0]], "|jccard:", jccard(hash_bSession_bought_item_list[records[0][0]], recommendations)

recommender_blog = Blog_Method()
list_score_BlogMethod = []
print "Start processing..."
scan_dataset("yoochoose-data/" + "yoochoose-clicks.dat", process_session_recommender_blog)

X = np.array(list_score_BlogMethod)
print "Average Score of Blog Method:", X.mean(), "std:", X.std()
# Average Score of Blog Method: 0.462245136117 std: 0.426082539886

def SmoothMean(X, n=100):
	x = []
	for i in range(0,len(X)-n):
		x.append(X[i:i+100].mean())
	return x
x = SmoothMean(X, n=100)
plt.plot(x)
plt.title("Blog Method Evaluation: SmoothMean over 100 points (Overlapped)")
plt.ylabel("Average Score")
plt.show()

# print sorted list of scores
list_score_BlogMethod.sort(reverse=True)
plt.plot(list_score_BlogMethod)
plt.title("Blog Method Evaluation: Sorted Score")
plt.ylabel("Score")
plt.xlim([0,600000])
plt.show()


# ====
# 1a TEST

def process_session_1a_test(records):
	if records[0][0] in hash_bSession_bought_item_list:
		hash_clicks_to_item = {}
		for record in records:
			if record[2] not in hash_clicks_to_item:
				hash_clicks_to_item[record[2]] = 1
			else:
				hash_clicks_to_item[record[2]] += 1
		list_item_sorted_increasing = [i[0] for i in sorted(hash_clicks_to_item.items(), key=operator.itemgetter(1), reverse=True)]

		recommendations = set(list_item_sorted_increasing[:int(hash_ratio_1a_ratio[len(records)]*len(records))])
		if len(recommendations) == 0:
			recommendations = set(list_item_sorted_increasing[0])
		list_score_1a.append(jccard(hash_bSession_bought_item_list[records[0][0]], recommendations))

hash_ratio_1a_ratio = {}
for i in hash_ratio_1a:
	hash_ratio_1a_ratio[i] = np.array(hash_ratio_1a[i]).mean()
list_score_1a = []
scan_dataset("yoochoose-data/" + "yoochoose-clicks.dat", process_session_1a_test)

X = np.array(list_score_1a)
print "Average Score of 1a (N item per click):", X.mean(), "std:", X.std()
# Average Score of 1a (N item per click): 0.576365714087 std: 0.368444600033

x = SmoothMean(X, n=100)
plt.plot(x)
plt.title("1a (N item per click) Evaluation: SmoothMean over 100 points (Overlapped)")
plt.ylabel("Average Score")
plt.show()

# print sorted list of scores
list_score_1a.sort(reverse=True)
plt.plot(list_score_1a)
plt.title("1a (N item per click) Evaluation: Sorted Score")
plt.ylabel("Score")
plt.xlim([0,600000])
plt.show()

# ====
# 1b TEST
hash_ratio_1b_ratio = {}
for i in hash_ratio_1b:
	hash_ratio_1b_ratio[i] = np.array(hash_ratio_1b[i]).mean()

list_score_1b = []
def process_session_1b_test(records):
	if records[0][0] in hash_bSession_bought_item_list:
		hash_clicks_to_item = {}
		for record in records:
			if record[2] not in hash_clicks_to_item:
				hash_clicks_to_item[record[2]] = 1
			else:
				hash_clicks_to_item[record[2]] += 1
		list_item_sorted_increasing = [i[0] for i in sorted(hash_clicks_to_item.items(), key=operator.itemgetter(1), reverse=True)]

		recommendations = set(list_item_sorted_increasing[:int(hash_ratio_1b_ratio[len(hash_clicks_to_item)]*len(hash_clicks_to_item))])
		if len(recommendations) == 0:
			recommendations = set(list_item_sorted_increasing[0])
		list_score_1b.append(jccard(hash_bSession_bought_item_list[records[0][0]], recommendations))

print "Start processing..."
scan_dataset("yoochoose-data/" + "yoochoose-clicks.dat", process_session_1b_test)

X = np.array(list_score_1b)
print "Average Score of 1b (N item per item viewed):", X.mean(), "std:", X.std()
# Average Score of 1b (N item per item viewed): 0.581956101794 std: 0.362297471217

x = SmoothMean(X, n=100)
plt.plot(x)
plt.title("1b (N item per item viewed) Evaluation: SmoothMean over 100 points (Overlapped)")
plt.ylabel("Average Score")
plt.show()

# print sorted list of scores
list_score_1b.sort(reverse=True)
plt.plot(list_score_1b)
plt.title("1b (N item per item viewed) Evaluation: Sorted Score")
plt.ylabel("Score")
plt.xlim([0,600000])
plt.show()
