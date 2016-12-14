import pickle
import time

class Message():
	"""
	A message, which is passed via messagequeue.
	"""
	def __init__(self, d):
		self.__dict__ = d
	
	@staticmethod
	def pickle(message):
		"""
		Pickle the message (dict) with the current timestamp.
		"""
		message["timestamp"] = time.time()
		return pickle.dumps(message)
	
	@staticmethod
	def unpickle(raw):
		"""
		Unpickle the message into a dict.
		"""
		return Message(pickle.loads(raw))
