import pytest

from bot.data import LogTargetFactory, LogTarget
from bot.mock import IDHolder
from bot.utils import Case

from .good_cases import (
	base_case,
	case_with_differents_all_comparable_attrs,
	case_with_differents_name,
	case_with_differents_name_and_act_and_target,
	case_with_differents_name_and_target,
	case_without_differents
)

target = IDHolder(8)
d_in = IDHolder(4)

def test_getComparableAttrs():
	test_instance = LogTarget(2, [target], "5", [d_in],
							  "sdq", None, None, None)
	comparable_attrs = test_instance._getComparableAttrs()
	expected_comparable_attrs = ['8', '5', '4', 'sdq']
	assert comparable_attrs == expected_comparable_attrs

@pytest.mark.parametrize(
	"args_for_first, args_for_second, expected_coincidence",
	[
		(base_case, case_without_differents, "1, 4, 3, 2, sudo"),
		(base_case, case_with_differents_name, "1, 4, 3, 2"),
		(base_case,
		 case_with_differents_name_and_target, "4, 3, 2"),
		(base_case,
		 case_with_differents_name_and_act_and_target, "3, 2"),
		(base_case,
		 case_with_differents_all_comparable_attrs, "")
	]
)
def test_getCoincidenceTo(
	args_for_first: Case,
	args_for_second: Case,
	expected_coincidence: str
):
	first_instance = LogTarget(**args_for_first)
	second_instance = LogTarget(**args_for_second)
	coincidence = first_instance.getCoincidenceTo(second_instance)
	assert coincidence == expected_coincidence

def test_LogTargetFabric():
	instance = LogTargetFactory(2, [target], ["5"], [d_in],
							  "sdq").getInstance()
	assert instance.priority is None
	assert instance.output is None
	assert instance.other is None

def test_LogTargetChangeMap():
	instance = LogTargetFactory(2, [target], ["5"], [d_in],
							  "sdq").getInstance()
	instance.priority = -1
	instance.output = -1
	instance.target = [IDHolder(87)]
	assert instance._change_map == {"priority": True, "output": True, "target":
		True}

def test_LogTargetIteration():
	instance = LogTargetFactory(2, [target], ["5"], [d_in],
							   "sdq").getInstance()
	instance.priority = -1
	instance.output = 56
	instance.target = [IDHolder(87)]
	for status, (field, _) in instance:
		if field in ["priority", "output", "target"]:
			assert status is True
		else:
			assert status is False