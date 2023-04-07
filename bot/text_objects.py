from typing import List, Optional

from .data import DataGroupAnalyzator, DataGroup

class SearchExpression:
	
	def __init__(self, string: str) -> None:
		self.string: List[str] = string.split(":")
		self.data_group: Optional['DataGroup'] = None

	def analyze(self) -> Optional['DataGroup']:
		self.extractDataGroup()
		return self.data_group

	def extractDataGroup(self) -> None:
		self.data_group = DataGroupAnalyzator(self.string[0]).analyze()

	def analyzeWildcard(self) -> None:
		if self.string[1] == "*":
			self.data_group.extractFromDB() # TODO определиться, как будет
			# передаваться изменения поведения при чтении из БД. Пока предлагается
			# указывать как аргумент в функции, но как она будет обрабатываться там?
			# Лучше передавать уже как какой-то готовый параметр, преобразованный
			# из Wildcard, которые сможет понять объект БД.