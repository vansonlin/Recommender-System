__author__ = 'vanson'

'''
Run parameter test for all 4 models.


Materials (for first stage):
	ItemFeatures/ItemFeatures_BuySessions_20k_Session1.txt
	ItemFeatures/ItemFeatures_Non-BuySessions_20k_Session1.txt

	ItemFeatures/ItemFeatures_BuySessions_20k_Session3.txt
	ItemFeatures/ItemFeatures_Non-BuySessions_20k_Session3.txt

	will produce the files for second stage
		0609SessionModelOnItem/0610SessionFeature_20k_20K1.txt
		0609SessionModelOnItem/0610SessionFeature_20k_20K3.txt

Materials (for second stage):
	Training set: 0609SessionModelOnItem/0610SessionFeature_20k_20K1.txt
	Testing set: 0609SessionModelOnItem/0610SessionFeature_20k_20K3.txt

Produce Experiment result file:
	0609SessionModelOnItem/0610summary_threshold_SessionTrain_on_ItemModel_All_Parameter.txt

'''

import time, random, operator, numpy as np
from sklearn.ensemble import GradientBoostingClassifier


def get_dataset_train_p1_n1(filepath):
	sessionIDs = []
	itemIDs = []
	y = []
	x = []

	f = open(filepath, "r")
	for line in f:
		line = line[:-1].split(",")
		if not line[2] == '0':
			sessionIDs.append(line[0])
			itemIDs.append(line[1])
			y.append(int(line[2]))
			x.append(map(float, line[3:]))
	f.close()
	return sessionIDs, itemIDs, y, x


def get_dataset_train_p1_0(filepath):
	sessionIDs = []
	itemIDs = []
	y = []
	x = []

	f = open(filepath, "r")
	for line in f:
		line = line[:-1].split(",")
		if not line[2] == '-1':
			sessionIDs.append(line[0])
			itemIDs.append(line[1])
			y.append(int(line[2]))
			x.append(map(float, line[3:]))
	f.close()
	return sessionIDs, itemIDs, y, x


def get_dataset_train_p1_n1_0(filepath):
	sessionIDs = []
	itemIDs = []
	y = []
	x = []

	f = open(filepath, "r")
	for line in f:
		line = line[:-1].split(",")
		sessionIDs.append(line[0])
		itemIDs.append(line[1])
		y.append(int(line[2]))
		x.append(map(float, line[3:]))
	f.close()
	return sessionIDs, itemIDs, y, x


def get_dataset_test(filepath):
	sessionIDs = []
	itemIDs = []
	y = []
	x = []

	f = open(filepath, "r")
	for line in f:
		line = line[:-1].split(",")
		sessionIDs.append(line[0])
		itemIDs.append(line[1])
		y.append(int(line[2]))
		x.append(map(float, line[3:]))
	f.close()
	return sessionIDs, itemIDs, y, x


def get_proba_arrays(sessionIDs_test, predict_proba):
	X = {}
	for ID, proba in zip(sessionIDs_test, predict_proba):
		if ID not in X:
			X[ID] = [proba]
		else:
			X[ID].append(proba)
	return X


def initilize_hash_feature_on_session(sessionIDs_test):
	hash_feature_on_session = {}
	for ID in sessionIDs_test:
		hash_feature_on_session[ID] = [[],[],[],[],[]]
	return hash_feature_on_session


def add_feature_to_session(hash_feature_on_session, X, index):
	for ID in X:
		array_proba = X[ID]
		hash_feature_on_session[ID][index] = [np.mean(array_proba)]
		for i in range(0,101, 10):
			hash_feature_on_session[ID][index].append(np.percentile(array_proba, i))


def add_feature_to_session_p1_n1(hash_feature_on_session, X, index):
	for ID in X:
		array_proba = sorted(X[ID], reverse=True)
		hash_feature_on_session[ID][index] = [np.mean(array_proba)]

		if len(array_proba) > 1:
			hash_feature_on_session[ID][index].append(array_proba[1])
			hash_feature_on_session[ID][index].append(array_proba[1]/array_proba[0])
		else:
			hash_feature_on_session[ID][index].append(array_proba[0])
			hash_feature_on_session[ID][index].append(1.)

		for i in range(0,101, 10):
			hash_feature_on_session[ID][index].append(np.percentile(array_proba, i))


def write_session_feature(filepath, hash_feature_on_session):
	f = open(filepath, "w")
	for ID in hash_feature_on_session:
		if ID in set_bSessionIDs:
			label = '+1'
		else:
			label = '-1'
		features = hash_feature_on_session[ID][0] + hash_feature_on_session[ID][1] + hash_feature_on_session[ID][2] \
				   + hash_feature_on_session[ID][3] + hash_feature_on_session[ID][4]
		f.write(ID + " " + label + " " + ",".join(map(str, features)) + "\n")
	f.close()


# def read_sessionFeature(filepath):
# 	sessionIDs = []
# 	y = []
# 	x = []
#
# 	f = open(filepath, "r")
# 	for line in f:
# 		line = line[:-1].split(" ")
# 		sessionIDs.append(line[0])
# 		y.append(int(line[1]))
# 		x.append(map(float, line[2].split(",")))
# 	f.close()
# 	return sessionIDs, y, x


def read_sessionFeature_from_hash(hash_feature_on_session):
	sessionIDs = []
	y = []
	x = []
	for ID in hash_feature_on_session:
		features = hash_feature_on_session[ID]
		sessionIDs.append(ID)

		if ID in set_bSessionIDs:
			y.append(1)
		else:
			y.append(-1)

		x.append(features[0] + features[1] + features[2] + features[3] + features[4])
	return sessionIDs, y, x


## Load Data
set_bSessionIDs = set(np.genfromtxt("yoochoose-data/sessionList_buying.txt", dtype=str))

sessionIDs_train_p1_n1, itemIDs_train_p1_n1, y_train_p1_n1, x_train_p1_n1 = get_dataset_train_p1_n1("ItemFeatures/ItemFeatures_train_10k1.txt")
sessionIDs_train_p1_0, itemIDs_train_p1_0, y_train_p1_0, x_train_p1_0 = get_dataset_train_p1_0("ItemFeatures/ItemFeatures_train_10k1.txt")
sessionIDs_train_p1_n1_0, itemIDs_train_p1_n1_0, y_train_p1_n1_0, x_train_p1_n1_0 = get_dataset_train_p1_n1_0("ItemFeatures/ItemFeatures_train_10k1.txt")

### Test set 1 in stage 1
sessionIDs_test_b_1, itemIDs_test_b_1, y_test_b_1, x_test_b_1 = get_dataset_test("ItemFeatures/ItemFeatures_BuySessions_20k_Session1.txt")
sessionIDs_test_n_1, itemIDs_test_n_1, y_test_n_1, x_test_n_1 = get_dataset_test("ItemFeatures/ItemFeatures_Non-BuySessions_20k_Session1.txt")

## Aggregated test dataset 1
# set_sessionIDs_buy = set(sessionIDs_test_b)
sessionIDs_test_1 = sessionIDs_test_b_1 + sessionIDs_test_n_1
itemIDs_test_1 = itemIDs_test_b_1 + itemIDs_test_n_1
y_test_1 = y_test_b_1 + y_test_n_1
x_test_1 = x_test_b_1 + x_test_n_1


### Test set 3 in stage 1
sessionIDs_test_b_3, itemIDs_test_b_3, y_test_b_3, x_test_b_3 = get_dataset_test("ItemFeatures/ItemFeatures_BuySessions_20k_Session3.txt")
sessionIDs_test_n_3, itemIDs_test_n_3, y_test_n_3, x_test_n_3 = get_dataset_test("ItemFeatures/ItemFeatures_Non-BuySessions_20k_Session3.txt")

## Aggregated test dataset 3
# set_sessionIDs_buy = set(sessionIDs_test_b_3)
sessionIDs_test_3 = sessionIDs_test_b_3 + sessionIDs_test_n_3
itemIDs_test_3 = itemIDs_test_b_3 + itemIDs_test_n_3
y_test_3 = y_test_b_3 + y_test_n_3
x_test_3 = x_test_b_3 + x_test_n_3

# Result Store
hash_feature_on_session_1 = initilize_hash_feature_on_session(sessionIDs_test_1)
hash_feature_on_session_3 = initilize_hash_feature_on_session(sessionIDs_test_3)

hash_clf_p1_n1 = {}
hash_clf_p1_0 = {}

f = open("0609SessionModelOnItem/0612summary_threshold_SessionTrain_on_ItemModel_All_Parameter_50.txt", "w")
f.write("\t".join(["n_est1", "rate1", "depth1", "n_est2", "rate2", "depth2", "n_est3", "rate3", "depth3", "n_est4", "rate4", "depth4", "thshd", "TP", "FP", "TN", "FN", "Prec", "Recall", "TP-FP", "T1", "T2", "T3", "T4"]) + "\n")
for n_estimator1 in [50]:
	for rate1 in [0.1, 0.3]:
		for depth1 in [2,3]:

			t1 = time.time()
			# Model p1_n1_0 training
			clf_p1_n1_0 = GradientBoostingClassifier(n_estimators=n_estimator1, learning_rate=rate1, max_depth=depth1, random_state=0)
			clf_p1_n1_0.fit(x_train_p1_n1_0, y_train_p1_n1_0)

			# Prediction of test 1 on Model p1_n1_0
			predict_proba_1 = clf_p1_n1_0.predict_proba(x_test_1)

			X = get_proba_arrays(sessionIDs_test_1, predict_proba_1[:,2])
			add_feature_to_session(hash_feature_on_session_1, X, 2)

			X = get_proba_arrays(sessionIDs_test_1, predict_proba_1[:,1])
			add_feature_to_session(hash_feature_on_session_1, X, 3)

			X = get_proba_arrays(sessionIDs_test_1, predict_proba_1[:,0]+predict_proba_1[:,2])
			add_feature_to_session_p1_n1(hash_feature_on_session_1, X, 4)

			#####

			# Prediction of test 1 on Model p1_n1_0
			predict_proba_3 = clf_p1_n1_0.predict_proba(x_test_3)

			X = get_proba_arrays(sessionIDs_test_3, predict_proba_3[:,2])
			add_feature_to_session(hash_feature_on_session_3, X, 2)

			X = get_proba_arrays(sessionIDs_test_3, predict_proba_3[:,1])
			add_feature_to_session(hash_feature_on_session_3, X, 3)

			X = get_proba_arrays(sessionIDs_test_3, predict_proba_3[:,0]+predict_proba_3[:,2])
			add_feature_to_session_p1_n1(hash_feature_on_session_3, X, 4)

			t1 = time.time() - t1

			for n_estimator2 in [100]:
				for rate2 in [0.3]:
					for depth2 in [3]:
						t2 = time.time()

						# Model p1_0 training
						if n_estimator2 + rate2 + depth2 not in hash_clf_p1_0:
							hash_clf_p1_0[n_estimator2 + rate2 + depth2] = GradientBoostingClassifier(n_estimators=n_estimator2, learning_rate=rate2, max_depth=depth2, random_state=0).fit(x_train_p1_0, y_train_p1_0)
						clf_p1_0 = hash_clf_p1_0[n_estimator2 + rate2 + depth2]
						# clf_p1_0 = GradientBoostingClassifier(n_estimators=n_estimator2, learning_rate=rate2, max_depth=depth2, random_state=0)
						# clf_p1_0.fit(x_train_p1_0, y_train_p1_0)

						# Prediction of test 1 on Model p1_0
						predict_proba_1 = clf_p1_0.predict_proba(x_test_1)
						X_1 = get_proba_arrays(sessionIDs_test_1, predict_proba_1[:,1])
						add_feature_to_session(hash_feature_on_session_1, X_1, 1)

						# Prediction of test 3 on Model p1_0
						predict_proba_3 = clf_p1_0.predict_proba(x_test_3)
						X_3 = get_proba_arrays(sessionIDs_test_3, predict_proba_3[:,1])
						add_feature_to_session(hash_feature_on_session_3, X_3, 1)

						t2 = time.time() - t2

						for n_estimator3 in [50, 100]:
							for rate3 in [0.1, 0.3]:
								for depth3 in [1,2,3]:
									t3 = time.time()

									# Model p1_n1 training
									if n_estimator3 + rate3 + depth3 not in hash_clf_p1_n1:
										hash_clf_p1_n1[n_estimator3 + rate3 + depth3] = GradientBoostingClassifier(n_estimators=n_estimator3, learning_rate=rate3, max_depth=depth3, random_state=0).fit(x_train_p1_n1, y_train_p1_n1)
									clf_p1_n1 = hash_clf_p1_n1[n_estimator3 + rate3 + depth3]
									# clf_p1_n1 = GradientBoostingClassifier(n_estimators=n_estimator3, learning_rate=rate3, max_depth=depth3, random_state=0)
									# clf_p1_n1.fit(x_train_p1_n1, y_train_p1_n1)

									# Prediction of test 1 on Model p1_n1
									predict_proba_1 = clf_p1_n1.predict_proba(x_test_1)
									X_1 = get_proba_arrays(sessionIDs_test_1, predict_proba_1[:,1])
									add_feature_to_session(hash_feature_on_session_1, X_1, 0)

									# Prediction of test 3 on Model p1_n1
									predict_proba_3 = clf_p1_n1.predict_proba(x_test_3)
									X_3 = get_proba_arrays(sessionIDs_test_3, predict_proba_3[:,1])
									add_feature_to_session(hash_feature_on_session_3, X_3, 0)

									t3 = time.time() - t3

									# Write session feature file
									# write_session_feature("0609SessionModelOnItem/0611SessionFeature_20k_20k1.txt", hash_feature_on_session_1)
									# write_session_feature("0609SessionModelOnItem/0611SessionFeature_20k_20k3.txt", hash_feature_on_session_3)

									# sessionIDs_train, y_train, x_train = read_sessionFeature("0609SessionModelOnItem/0611SessionFeature_20k_20k1.txt")
									# sessionIDs_test, y_test, x_test = read_sessionFeature("0609SessionModelOnItem/0611SessionFeature_20k_20k3.txt")

									sessionIDs_train, y_train, x_train = read_sessionFeature_from_hash(hash_feature_on_session_1)
									sessionIDs_test, y_test, x_test = read_sessionFeature_from_hash(hash_feature_on_session_3)

									for n_estimator4 in [50, 100]:
										for rate4 in [0.1, 0.3]:
											for depth4 in [2,3]:
												t4 = time.time()

												clf = GradientBoostingClassifier(n_estimators=n_estimator4, learning_rate=rate4, max_depth=depth4, random_state=0)
												clf.fit(x_train, y_train)
												predict_proba = clf.predict_proba(x_test)[:,1]

												t4 = time.time() - t4

												print "Time:", ",".join(map(str,[int(t1), int(t2), int(t3), int(t4)])), "|", n_estimator1, rate1, depth1, "|", n_estimator2, rate2, depth2, "|", n_estimator3, rate3, depth3, "|", n_estimator4, rate4, depth4, "|", time.ctime()

												for threshold in np.arange(0.4, 0.61, 0.02):
													TP = 0
													FP = 0
													TN = 0
													FN = 0
													for tv, proba in zip(y_test, predict_proba):
														if proba > threshold:
															pv = 1
														else:
															pv = -1

														if pv == 1:
															if tv == 1:
																TP += 1
															else:
																FP += 1
														else:
															if tv == 1:
																FN += 1
															else:
																TN += 1
													f.write("\t".join([str(n_estimator1), str(rate1), str(depth1), str(n_estimator2), str(rate2), str(depth2), str(n_estimator3), str(rate3), str(depth3), str(n_estimator4), str(rate4), str(depth4), str(threshold), str(TP), str(FP), str(TN), str(FN), str(round(TP*1./(TP+FP), 3)), str(round(TP*1./(TP+FN), 3)), str(TP-FP), str(int(t1)), str(int(t2)), str(int(t3)), str(int(t4))]) + "\n")

f.close()


####
