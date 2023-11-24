

from bot.data import ActGroup


def test_identificator():
	instance = ActGroup()
	assert instance.DB_IDENTIFICATOR == "act"

def test_extractData_act_group():
	instance = ActGroup()
	assert instance.extractData() == [""]