__author__ = 'vanson'
'''
Input sessionID of interests list
'''

class ItemClickTransitionMethod:
	def __init__(self, session_targeted_list, click_distribution=True):
		# dict: itemID -> all values in that row, as well as the itemID with max val
		self.session_set = set(session_targeted_list)
		self.item_matrix = ItemMatrixCSRReader("associatedResult/" + "ItemItemMatrix_1basedCSR_probability.txt")
		self.session_click_flow = {} # dict: sessionID -> [itemID1, itemID2, itemID3, ...] item click flow over that session
		self.__build_session_click_flow_dict()

		self.recommendation_pred = []
		self.recommendation_pred_score = [] # normalized by max
		self.recommend_bulk(session_targeted_list)

		self.recom_click_pred = []
		self.recom_click_pred_score = [] # normalized by max
		if click_distribution == True:
			self.compute_click_probability_bulk(session_targeted_list)

	def __build_session_click_flow_dict(self, filename="yoochoose-data/yoochoose-clicks.dat"):
		f = open(filename, "r")
		raw_line = f.readline()
		while len(raw_line) > 1:
			line = raw_line[:-1].split(",")
			if int(line[0]) in self.session_set: # if is target session
				self.session_set.remove(int(line[0]))
				sessionID = int(line[0])
				click_flow = [int(line[2])]
				raw_line = f.readline()
				while len(raw_line) > 1:
					line = raw_line[:-1].split(",")
					if int(line[0]) != sessionID:
						break
					else:
						click_flow.append(int(line[2]))
						raw_line = f.readline()
				self.session_click_flow[sessionID] = click_flow
				if len(self.session_set) == 0:
					break # break while
			else:
				raw_line = f.readline()
		f.close()

	def recommend_bulk(self, sessions):
		for session in sessions:
			pred_item_score = self.__recommendation(session)
			self.recommendation_pred.append([i[0] for i in pred_item_score])
			max_score = max([i[1] for i in pred_item_score])
			self.recommendation_pred_score.append([i[1]*1./max_score for i in pred_item_score])

	def __recommendation(self, session):
		import operator
		items_dict = {}
		for itemID in self.session_click_flow[session]:
			predicted_item = self.__extract_most_next_item(itemID)
			if items_dict.has_key(predicted_item[0]):
				items_dict[predicted_item[0]] += predicted_item[1]
			else:
				items_dict[predicted_item[0]] = predicted_item[1]
		sorted_items_dict = sorted(items_dict.items(), key=operator.itemgetter(1), reverse=True)
		return sorted_items_dict

	def compute_click_probability_bulk(self, sessions):
		for session in sessions:
			recommendation_score = self.__compute_click_probability(session)
			self.recom_click_pred.append([i[0] for i in recommendation_score])
			max_score = max([i[1] for i in recommendation_score])
			self.recom_click_pred_score.append([i[1]*1./max_score for i in recommendation_score])

	def __compute_click_probability(self, session):
		import operator
		item_count_dict = {}
		for item in self.session_click_flow[session]:
			if item_count_dict.has_key(item):
				item_count_dict[item] += 1
			else:
				item_count_dict[item] = 1
		sorted_items_click_dict = sorted(item_count_dict.items(), key=operator.itemgetter(1), reverse=True)
		return sorted_items_click_dict

	def __extract_most_next_item(self, itemID):
		next_itemID = self.item_matrix.CSRmatrix[itemID]["max"]
		return [next_itemID, self.item_matrix.CSRmatrix[itemID][next_itemID]]

class ItemMatrixCSRReader:
	def __init__(self, CSR_filename, header=20, item_list_filename="yoochoose-data/itemList.txt"):
		self.itemList = itemList(item_list_filename)
		self.itemID_to_index = self.itemList.itemID_to_index # dict, 0-based index
		self.index_to_itemID = self.itemList.index_to_itemID # dict, 0-based index

		self.CSRmatrix = {} # dict of dict: itemID -> itemID -> score
		self.read_CSR_file(CSR_filename, header)

	def read_CSR_file(self, CSR_filename, header):
		f = open(CSR_filename)
		for i in range(header):
			f.readline()
		n_row, n_col, nnz = map(int, f.readline()[:-1].split(" "))
		index = 0 # 0-based
		for line in f:
			line = line[:-1].split(" ")
			item_dict = {}
			max_id = None
			max_val = -100.
			for i in range(len(line)/2):
				item_id = self.index_to_itemID[int(line[2*i])-1] # line[2*i] is 1-based index
				val = float(line[2*i+1])
				if val > max_val:
					max_id = item_id
					max_val = val
				item_dict[item_id] = val
			item_dict["max"] = max_id
			self.CSRmatrix[self.index_to_itemID[index]] = item_dict
			index += 1
		f.close()

		if n_row != index:
			print "item matrix CSR file is not correct!\n"


class itemList:
	'''
		0-based index
	'''
	def __init__(self, item_list_filename):
		self.itemID_to_index = None
		self.index_to_itemID = None
		self.read_file(item_list_filename)

	def read_file(self, item_list_filename):
		f = open(item_list_filename, "r")
		self.itemID_to_index = {}
		self.index_to_itemID = {}
		i = 0
		for line in f:
			itemID = int(line[:-1])
			self.itemID_to_index[itemID] = i
			self.index_to_itemID[i] = itemID
			i += 1

# a = ItemClickTransitionMethod([1,3,6,11])

