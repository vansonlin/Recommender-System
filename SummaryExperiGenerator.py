__author__ = 'vanson'

"""
Task 1:
	Use libsvm to predict the buying session, and pass the predicted buying session to task 2

Task 2:
	Predict three set of recommendations based on blog method.

	The Blog method:
	1. scan the buying dataset, and collect all the items which were bought more than NBought times (target item base).
	2. scan the testing click dataset, and extract sessions which have intersection with the target item base.


"""
from ItemRecommender.ItemClickTransitionMethod import ItemClickTransitionMethod
from ItemRecommender.getBoughtItemList import getBoughtItemList
from ItemRecommender.Evaluation import Evaluation
from feature_generator.Feature_Normalizer import FeatureNormalizer
from ItemRecommender.ClickDistributionMethod import ClickDistributionMethod
from libsvm.python.svmutil import *
from ItemRecommender.Evaluation import Evaluation
from samples.TrueAnswerGenerator import get_whole_true_answer
import time
import numpy as np
##### Task 1
# predict buying sessions

def write_record(f, attributes, record):
	'''

	:param f: opened file object
	:param attributes: a list of attribute, each element is a key to the record in order
	:param record: record for that line
	'''
	f.write("\t".join([record[i] for i in attributes])+"\n")
	return

def get_item_over_NClick(clicked_items, NClick):
	if NClick == 1:
		return np.unique(clicked_items)
	item_count = {}
	for i in clicked_items:
		if item_count.has_key(i):
			item_count[i] += 1
		else:
			item_count[i] = 1
	return [i for i in item_count if item_count[i] >= NClick]

def build_item_count_list():
	'''
	from the pre-built item count file,
	generates 4 sets which contains itemIDs which were bought N times above (inclusive)
	'''
	item_bought_N_above = {5:set(), 10:set(), 20:set(), 40:set()}
	f = open("yoochoose-data/BoughtItemCount.txt", "r")
	for line in f:
		line = map(int, line[:-1].split(","))
		if line[1] >= 40:
			item_bought_N_above[40].add(line[0])
			item_bought_N_above[20].add(line[0])
			item_bought_N_above[10].add(line[0])
			item_bought_N_above[5].add(line[0])
		elif line[1] >= 20:
			item_bought_N_above[20].add(line[0])
			item_bought_N_above[10].add(line[0])
			item_bought_N_above[5].add(line[0])
		elif line[1] >= 10:
			item_bought_N_above[10].add(line[0])
			item_bought_N_above[5].add(line[0])
		elif line[1] >= 5:
			item_bought_N_above[5].add(line[0])
	return item_bought_N_above


print "Initializing Experiment ", time.ctime()
# buyingSessionList = np.genfromtxt("yoochoose-data/sessionList_buying.txt", dtype=int) # only the buy sessions
buyingSessionList = np.genfromtxt("yoochoose-data/sessionList_clicks.txt", dtype=int) # all sessions
a = ClickDistributionMethod(buyingSessionList, "yoochoose-data/yoochoose-clicks.dat")
buying_click_flow = a.session_click_flow # dict: sessionID -> click flow in list format

true_items = get_whole_true_answer() # dict: sessionID -> bought item list

item_bought_N_above = build_item_count_list() # itemID list which each item was bought over 5, 10, 20, 40 times

dr = "samples/"
filenames = [	"feature_set_sample_5k1_extra_blog.txt",
				"feature_set_sample_5k2_extra_blog.txt",
				"feature_set_sample_5k3_extra_blog.txt",
				"feature_set_sample_5k4_extra_blog.txt",
				"feature_set_sample_5k5_extra_blog.txt",
				"feature_set_sample_5k6_extra_blog.txt",
				"feature_set_sample_10k1_extra_blog.txt",
				"feature_set_sample_10k2_extra_blog.txt",
				"feature_set_sample_10k3_extra_blog.txt",
				"feature_set_sample_10k4_extra_blog.txt",
				"feature_set_sample_10k5_extra_blog.txt",
				"feature_set_sample_10k6_extra_blog.txt"]

print "Start Experimenting ", time.ctime()

f = open("Result_RBF_Blog_Method_With_Blog_Attri.txt", "w") # file name
f.write("Results of feature sets with additional blog method attribute (5 for buying, 0 otherwise). And only normalizing count-based features. Sessions predicted with RBF model, and recommended by blog method.\n\n")

gammas = [1, 10, 100, 1000]

attributes = ["SamFile","Md","Para","Norm","Thshd","TP","TN","FP","FN","Prec","Recall","ACC","ROC","(TP-FP)", "c","Sscore","NClick","NBought","Iscore", "ExtraFP", "ExtraTP","SCORE","Time"]
f.write("\t".join(attributes)+"\n")
for gamma in gammas:
	# for i in range(len(filenames)):
	for i in range(len(filenames)):
	# for i in range(2):
		print time.ctime()
		# print "RBF kernel with max normalization, gamma="+str(gamma)+"\n" \
		print "RBF kernel with max normalization\n" \
			  "Sample Filename:", filenames[i]

		record = {}
		record["SamFile"] = filenames[i].split(".")[0][19:-8] # SamFile
		record["Md"] = "RBF" # model type
		record["Para"] = str(gamma) # parameter
		record["Norm"] = "max"

		fn = FeatureNormalizer(dr + filenames[i], normalization="max", header=39) # read data and normalize it by max

		y = fn.label
		x = fn.feature_set

		training_protion = int(len(y)*0.8)
		x_train = x[:training_protion]
		y_train = y[:training_protion]
		x_test = x[training_protion:]
		y_test = y[training_protion:]

		sessionID_test = fn.sessionID[training_protion:]

		t = time.time()
		# m = svm_train(y_train, x_train, "-t 0 -q") # linear kernel, training
		m = svm_train(y_train, x_train, "-t 2 -g "+str(gamma)+" -q") # RBF kernel with gamma value, training
		# m = svm_train(y, x, "-t 0 -v 5") # linear kernel, 5 fold cross validation
		# m = svm_train(y, x, "-t 2 -v 5 -g 1000") # RBF kernel, 5 fold cross validation

		# modelname = "rbf_"+str(gamma)+"_max_" + filenames[i].split(".")[0][19:] + ".libsvm"
		modelname = "rbf_max_" + filenames[i].split(".")[0][19:-8] + ".libsvm"
		svm_save_model("model/" + modelname, m)
		# m = svm_load_model("model/" + modelname)

		result = svm_predict(y_test, x_test, m, record) # prediction buying session (1/-1), return label, evaluation, probability

		record["Time"] = str(round(time.time() - t, 2))
		for threshold in [-0.4, -0.2, 0, 0.2]:
			record["Thshd"] = str(threshold)
			predicted_labels = [1 if i[0] >= threshold else -1 for i in result[2]]

			ev = Evaluation()
			ev.general(y_test, predicted_labels, record)

			TP = int(record["TP"])
			FP = int(record["FP"])
			record["(TP-FP)"] = str(TP - FP)

			roc_auc = ev.ROC(y_test, [i[0] for i in result[2]])
			record["ROC"] = str(round(roc_auc, 4))

			c = (TP + float(record["FN"]))/len(y_test)
			record["Sscore"] = str(round((TP - FP)*c, 2))  # normalized by size of testing data, and then times 1000

			for NClick in [1,2,3]:
				for NBought in [5,10,20,40]:
					record["NClick"] = str(NClick)
					record["NBought"] = str(NBought)
					Iscore = 0.

					result_zip = zip(fn.sessionID[training_protion:], y_test, predicted_labels)
					ExtraFP = 0.
					ExtraTP = 0.
					for sessionID, tv, pv in result_zip:
						if pv == 1 and tv == -1:
							items_NClick_above = get_item_over_NClick(buying_click_flow[sessionID], NClick)
							predicted_items = list(item_bought_N_above[NBought].intersection(items_NClick_above))
							if len(predicted_items) == 0: # this session will be removed because no recommendation available
								ExtraFP += c
						elif tv == 1 and pv == 1:
							items_NClick_above = get_item_over_NClick(buying_click_flow[sessionID], NClick)
							predicted_items = list(item_bought_N_above[NBought].intersection(items_NClick_above))
							# predicted_items = np.intersect1d(items_NClick_above, item_bought_N_above[NBought])
							Iscore += ev.Jaccard(true_items[sessionID],predicted_items)
							if len(predicted_items) == 0:
								ExtraTP -= c
					record["c"] = str(round(c, 4))
					record["Iscore"] = str(round(Iscore, 2))
					record["ExtraFP"] = str(round(ExtraFP, 2))
					record["ExtraTP"] = str(round(ExtraTP, 2))

					record["SCORE"] = str(round((TP - FP)*c + Iscore + ExtraFP + ExtraTP, 2)) # sum of Sscore, Iscore, ExtraSs
					write_record(f, attributes, record)

		print "Model file name:", modelname
		print "Completition Time:", time.time() - t
		# write_record(f, attributes, record)
		print "----------------------------\n"

f.close()
print "Done"


###
# trial adaboosting
from sklearn.cross_validation import cross_val_score
from sklearn.datasets import load_iris
from sklearn.ensemble import AdaBoostClassifier

fn = FeatureNormalizer(dr + "feature_set_sample_5k1_extra_blog.txt", normalization="max", header=39) # read data and normalize it by max

y = fn.label
x = fn.feature_set
x = [[x[i][j] for j in x[i]] for i in range(len(x))] # convert to array like format

training_protion = int(len(y)*0.8)
x_train = x[:training_protion]
y_train = y[:training_protion]
x_test = x[training_protion:]
y_test = y[training_protion:]

clf = AdaBoostClassifier()
clf.fit(x_train, y_train)
result_prob = clf.predict_proba(x_test)

scores = cross_val_score(clf, x, y)