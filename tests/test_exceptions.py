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
	instance = UnmatchingParameterTypeError("test", "test2", Text)
	assert instance.getText() == ("Значение \"{}\" не соответствует типам: {} в параметре \"{}\". Пожалуйста,"
		"измените значение параметра, либо укажите параметр явно.").format("test", Text, "test2")