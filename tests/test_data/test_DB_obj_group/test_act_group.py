

from bot.data import ActGroup


def test_extractData_act_group():
	instance = ActGroup()
	assert instance.extractData() == [""]