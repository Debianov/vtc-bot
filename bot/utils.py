from inspect import getfullargspec
from typing import Dict, Callable, Any, Union, Tuple, List

# from bot.objects.commands import Required
# from bot.objects.text import Text

def getCallSignature(instance: Callable[[Any], Any]) -> Dict[str, Any]:
	result: Dict[str, Union[str, Tuple[Any]]] = {} # Dict[str, Union[str, Tuple[Required, Text]]] убрал, поскольку надо было убрать import Required из-за циклического импортирования.
	# TODO сделать выше нужно будет кастом generic, либо как-нибудь вернуть Dict[str, Union[str, Tuple[Required, Text]]].
	check_obj = instance
	key_exceptions = ["channel", "self", "return"]
	arg_spec = getfullargspec(check_obj)
	for parameter in arg_spec.args:
		if parameter not in key_exceptions:
			result[parameter] = ""
	for (parameter, annotation) in arg_spec.annotations.items():
		if parameter not in key_exceptions:
			result[parameter] = annotation
	return result

def getKeyByValue(collection: Dict[Any, Any], check_value: Any) ->\
Dict[Any, Any]:
	new_collection = {}
	for (key, value) in collection.items():
		if value == check_value:
			new_collection[key] = value
	return new_collection

class ArgAndParametersList(list):

	def prepare(self) -> None:
		generator = super().__iter__()
		for (current_ind, element) in enumerate(generator): #! временное решение, пока не ликвидировал все 
			# проблемы при split-инге.
			if element == " ":
				super().remove(" ")

	def popWithSpaceRemoving(self, index: int) -> Any: #! временное решение, пока не ликвидировал все
		# проблемы при split-инге.
		poped_object = super().pop(index)
		return poped_object.strip(" ")

def isDigitWithSpace(string: str, excepts: List[str]) -> bool:
	for symbol in string:
		if symbol in excepts + [" "]:
			pass 
		elif not symbol.isdigit():
			return False
	return True

def getBracketNotationStatus(string: str, open_bracket: str, close_bracket: str) -> bool:
	stack = []
	for symbol in string:
		if symbol == open_bracket:
			stack.append(symbol)
		elif symbol == close_bracket:
			try:
				stack.pop()
			except IndexError:
				return False
	if stack:
		return False
	return True