class ChannelMentionText: 

	def __init__(self, text: str) -> str:
		if text.startswith("#"):
			return text
		else:
			raise Exception # TODO

class StrOrIntText: #! якорь

	def __init__(self, text: str) -> str:
		if text.isalnum():
			return text
		else:
			raise Exception # TODO