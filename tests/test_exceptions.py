import pytest

from bot.objects.exceptions import ParameterError, UnmatchingParameterTypeError
from bot.objects.text import Text


@pytest.mark.parametrize(
	"parameter_name", [
		"test",
		"d_test"
	]
)
def test_parameter_error(parameter_name) -> None:
	instance = ParameterError(parameter_name)
	assert instance.getText() == ""
	assert instance.getParameterName() == parameter_name.removeprefix("d_")

def test_unmatching_parameter_type_error() -> None:
	instance = UnmatchingParameterTypeError("test", ("test2", Text))
	assert instance.getText() == ("Тип \"{}\" не соответствует значению \"{}\" в параметре"
		" \"{}\". Пожалуйста, исправьте значение.").format(Text, "test", "test2")

