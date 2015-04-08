__author__ = 'vanson'


class Evaluation:
	def HR(self, prediction, true):
		'''
		each of arguments is 2d list.
		each row in the list is the itemID of that session.

		Hit-rate:
		number of sessions with hit / number of total sessions

		:param prediction:
		:param true:
		:return:
		'''
		n = 0
		for i in range(len(prediction)):
			if len(true[i]) == 0:
				continue
			for item in prediction[i]:
				if item in true[i]:
					n += 1
					break
		return n*1./len(prediction)

# a = [[1,2,3],
# 	 [],
# 	 [5,4]]
#
# true = bought_item_list

