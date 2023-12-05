from bot.mock import IDHolder
from bot.utils import Case, DelayedExpression

case_without_none = Case(
	dbconn=DelayedExpression("db"),
	context_id=1,
	target=IDHolder(1),
	act=IDHolder(1),
	d_in=[IDHolder(3), IDHolder(2)],
	name="sudo",
	output="deb",
	priority=2,
	other=2,
	dbrecord_id=3
)

case_with_none = Case(
	dbconn=DelayedExpression("db"),
	context_id=1,
	target=IDHolder(1),
	act=IDHolder(1),
	d_in=[IDHolder(3), IDHolder(2)],
	name=None,
	output=None,
	priority=None,
	other=None,
	dbrecord_id=None
)

expect_case_for_case_with_none = case_with_none
expect_case_for_case_with_none["dbrecord_id"] = 0

case_with_none_except_db_record_id = Case(
	dbconn=DelayedExpression("db"),
	context_id=1,
	target=IDHolder(1),
	act=IDHolder(1),
	d_in=[IDHolder(3), IDHolder(2)],
	name=None,
	output=None,
	priority=None,
	other=None,
	dbrecord_id=1
)