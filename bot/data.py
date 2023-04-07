from typing import List, Optional, Any, Final, Callable, Tuple

class DataGroupAnalyzator:
	
	def __init__(self, string) -> None:
		self.split_string: List[str] = string.split("+")
		self.definited_groups: Optional[DataGroup] = None

	def analyze(self) -> 'DataGroup':
		to_check: List[DataGroup] = DataGroup.__subclasses__()
		copy_string: List[str] = self.split_string
		check_string_limit: int = 0
		for group_name in copy_string:
			for group_type in to_check:
				group_instance = group_type()
				if group_name == group_instance:
					if not self.definited_groups:
						self.definited_groups = group_instance
					else:
						self.definited_groups += group_instance
					break
		return self.definited_groups

class DataGroup:
	
	IDENTIFICATOR: str = ""

	def __init__(self) -> None:
		# что-то связанное с БД...
		pass

	def __eq__(self, right_operand: Any) -> bool:
		return self.IDENTIFICATOR == right_operand

	def __add__(self, right_operand: Any) -> Optional['DataGroup']:
		if isinstance(right_operand, DataGroup):
			constructing_instance: DataGroup = DataGroup()
			constructing_instance.IDENTIFICATOR = self.IDENTIFICATOR + "," + right_operand.IDENTIFICATOR
			constructing_instance.extractFromDB = lambda: (self.extractFromDB(), right_operand.extractFromDB())
			return constructing_instance
		raise TypeError(right_operand)

	def extractFromDB(self) -> None:
		pass

class UserGroup(DataGroup):

	IDENTIFICATOR: Final = "usr"

	def extractFromDB(self) -> None:
		pass

class ChannelGroup(DataGroup):

	IDENTIFICATOR: Final = "ch"

	def extractFromDB(self) -> None:
		pass