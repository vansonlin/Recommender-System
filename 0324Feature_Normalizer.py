__author__ = 'vanson'
'''
number of buying session:    509696
number of all session:      9249729
'''

class FeatureNormalizer:
	def __init__(self, filename, header = 35, normalization="max"):
		self.nrows_header = header
		self.filename = filename

		self.feature_set = None
		self.label = None
		self.sessionID = None

		self.max_list = None
		if normalization == "max":
			self.normalization_max()

		self.sum_list = None
		if normalization == "sum":
			self.normalization_sum()

		self.svd = None
		self.mean_list = None
		if normalization == "mean":
			self.normalization_mean()

	def __get_sum(self):
		f = open(self.filename, "r")
		for i in range(self.nrows_header):
			f.readline()
		line = f.readline()
		self.sum_list = [0.] * (len(line[:-1].split(",")) - 2)
		while len(line) > 1:
			line = map(float, line[:-1].split(",")[2:])
			for i in range(len(line)):
				self.sum_list[i] += line[i]
			line = f.readline()
		f.close()

	def __get_max(self):
		f = open(self.filename, "r")
		for i in range(self.nrows_header):
			f.readline()
		self.max_list = [-100.]*36
		n = 0
		for line in f:
			n += 1
			line = map(float, line[:-1].split(",")[2:])
			for i in range(len(line)):
				if line[i] > self.max_list[i]:
					self.max_list[i] = line[i]
		f.close()

	def __get_mean(self):
		self.__get_sum()
		n = 0.

		f = open(self.filename, "r")
		for line in f: # count number of lines
			n += 1
		f.close()

		self.mean_list = []
		for i in self.sum_list:
			self.mean_list.append(i/n)

	def normalization_mean(self):
		self.__get_mean()
		self.normalization(self.mean_list)

	def normalization_max(self):
		self.__get_max()
		self.normalization(self.max_list)

	def normalization_sum(self):
		self.__get_sum()
		self.normalization(self.sum_list)

	def normalization(self, normalizator):
		f = open(self.filename, "r")
		for i in range(self.nrows_header):
			f.readline()
		self.label = []
		self.feature_set = []
		self.sessionID = []
		for line in f:
			line = line[:-1].split(",")
			self.sessionID.append(int(line[0])) # session ID goes here
			line = map(float, line[1:]) # exclude session ID
			self.label.append(line[0])
			feature = {}
			for i in range(len(line)-1):
				feature[i+1] = line[i+1]/normalizator[i]
				# feature.append(line[i+1]/self.max_list[i])
			self.feature_set.append(feature)

