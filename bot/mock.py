
import psycopg


class Mock:
	pass

class MockAsyncConnection(psycopg.AsyncConnection, Mock):
	"""
	A mock class for `BotConstructor`.
	"""
	
	def __init__(self):
		pass