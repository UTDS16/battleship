import pickle
import time

# Server announce message.
M_ANNOUNCE = 0x00
# Client join message.
M_JOINING = 0x01
# Generic acknowledge.
M_ACK = 0x0A
# Generic error message.
M_NACK = 0xFF

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
