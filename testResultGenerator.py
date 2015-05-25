__author__ = 'vanson'

'''
This source file is use to generate the competition result based on the provided test.dat
It takes the following files for input:

1. libsvm model file for model input
2. test feature file (For Task 1: to generate predicted buying sessions)
3. the test click file (For Task 2: to generate recommended items for each predicted buying session based on click flow)

Data Description for Test Data set:
Number of Sessions: 2,312,432
Number of Clicks: 8,251,791

Procedures:
1. predict buying sessions based on 6 models (10k, rfb, 10000)
2. re-calculate the label based on score and threshold (score > threshold -> buying where threshold is negative)
3. combine the labels, and only consider 4 or more predicted buy as buying sessions
4. make recommended item list (Top N popular where N = 2 or item score over 0.3)
5. save in submission format, and submit
'''

from ItemRecommender.ItemClickTransitionMethod import ItemClickTransitionMethod # Method 1
from ItemRecommender.ClickDistributionMethod import ClickDistributionMethod # Method 3
from feature_generator.Feature_Normalizer import FeatureNormalizer
from libsvm.python.svmutil import *
import time


#################################################
### Task 1 : Generate predicted buy sessions ####
#################################################

fn = FeatureNormalizer("samples/feature_set_test.txt", header = 33, normalization="max") # Real Test file only has 33 lines for header
# fn = FeatureNormalizer("samples/feature_set_test_50k.txt", header = 35, normalization="max") # Real Test file only has 33 lines for header
sessionIDs = fn.sessionID
x = fn.feature_set
y = [0]*len(x)

dr = "model/"
modelfile = "linear_max_10k_2.libsvm"
m = svm_load_model(dr + modelfile)

# threshold = -0.1 # threshold for score to be categorized to buy (negative indicates higher recall)

print time.ctime()
t = time.time()
f = open("123.txt", "w") # trivial
result = svm_predict(y,x,m,f)
f.close() # trivial
print time.time() - t

print
n = 0
for i in result[2]:
	if i[0] > 0:
		n+=1
print n, n*1./len(y)
print

### save predicted labels and scores in the same order of feature_set_test.txt
f = open("test_linear_10k2_label_score.txt", "w")
for i in range(len(result[0])):
	f.write(str(sessionIDs[i]) + "," + str(int(result[0][i])) + "," + str(result[2][i][0])+"\n")
f.close()
print "Done"
print time.ctime()

############################################
### Task 2 : Predict which items to buy  ###
############################################
f1 = open("test_linear_5k2_label_score.txt", "r")
f2 = open("test_linear_10k2_label_score.txt", "r")
buySession1 = []
buySession2 = []
while True:
	line1 = f1.readline()
	line2 = f2.readline()
	if len(line1) < 1 or len(line2) < 1:
		break
	line1 = line1[:-1].split(",")
	line2 = line2[:-1].split(",")
	if line1[1] == "1":
		buySession1.append(int(line1[0]))
	if line2[1] == "1":
		buySession2.append(int(line2[0]))
f1.close()
f2.close()

label_union = set(buySession1 + buySession2) # submission 1

set1 = set(buySession1)
set2 = set(buySession2)
label_intersection = set1.intersection(set2) # submission 2

sessionIDs1 = list(label_union)
sessionIDs2 = list(label_intersection)
items1 = ClickDistributionMethod(sessionIDs1, "yoochoose-data/yoochoose-test.dat")
items2 = ClickDistributionMethod(sessionIDs2, "yoochoose-data/yoochoose-test.dat")

def create_submission(filename, sessionIDs, itemsOb):
	f = open(filename, "w")
	for i in range(len(sessionIDs)):
		f.write(str(sessionIDs[i])+";")
		items = itemsOb.recom_click_pred[i][:20]
		f.write(str(items[0]))
		for item in items[1:]:
			f.write(","+str(item))
		f.write("\n")
	f.close()

create_submission("submission_union_20.txt", sessionIDs1, items1)
create_submission("submission_intersection_20.txt", sessionIDs2, items2)

