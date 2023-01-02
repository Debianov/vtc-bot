import typing

from utils import getCallSignature

# class MenuParser(Parser):

# 	def __init__(self, point: str, content: typing.Iterable,
# name_extraction_object: dict):
# 		super().__init__(content, name_extraction_object)
# 		self.point = point

# 	def getCommand(self):
# 		for point_names in self.name_extraction_object:
# 			print(point_names)
# 			point_names_collection = point_names.split("|")
# 			if self.point in point_names_collection:
# 				self.exemplar_and_method = self.name_extraction_object[point_names]
# 		return self.exemplar_and_method

class ActElement:

	def __init__(self) -> None:
		self.checking_symbol: str = ""
		self.bind_act: str = ""

	def determineAct(self) -> None:
		match self.checking_symbol:
			case '+':
				self.bind_act = "ADD"
			case '-':
				self.bind_act = "DELETE"
			case '>':
				self.bind_act = "CHANGE"

special_symbols = ["+", "-", "%", ">"]