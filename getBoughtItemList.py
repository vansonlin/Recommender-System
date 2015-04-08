__author__ = 'vanson'


class getBoughtItemList:
	def __init__(self, sessions):
		self.sessions = sessions
		self.sessions_set = set(sessions)
		self.session_index = {}
		self.build_session_index(sessions)

		self.bought_item_list = [[]]*len(sessions)
		self.get_bought_item()

	def build_session_index(self, sessions):
		for i in range(len(sessions)):
			self.session_index[sessions[i]] = i

	def get_bought_item(self):
		f = open("yoochoose-data/" + "yoochoose-buys.dat", "r")
		raw_line = f.readline()
		while len(raw_line) > 1 and len(self.sessions_set) > 0:
			line = raw_line[:-1].split(",")
			if int(line[0]) in self.sessions_set:
				label = int(line[0]) # new session found
				self.sessions_set.remove(label)
				item_list = [int(line[2])]

				raw_line = f.readline() # read new line
				while len(raw_line) > 1 and  int(raw_line.split(",")[0]) == label: # if new line is in same session
					line = raw_line[:-1].split(",")
					item_list.append(int(line[2]))
					raw_line = f.readline() # read new line
				self.bought_item_list[self.session_index[label]] = item_list
			else:
				raw_line = f.readline()
		f.close()