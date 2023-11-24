
import psycopg

from ._types import IDSupportObjects


class Mock:
	pass

class MockAsyncConnection(psycopg.AsyncConnection, Mock):
	"""
	A mock class for `BotConstructor`.
	"""
	
	def __init__(self):
		pass

class IDHolder(Mock, IDSupportObjects):

	def __init__(self, id):
		self.id = id