from bot.mock import IDHolder
from bot.utils import Case, DelayedExpression

base_case = Case(
	guild_id=2,
	target=[IDHolder(1)],
	act=[IDHolder(4)],
	d_in=[IDHolder(3), IDHolder(2)],
	name="sudo",
	output="deb",
	priority=2,
	other=2
)

case_without_differents = base_case

case_with_differents_name = base_case.copy()
case_with_differents_name.update({"name": "aboba"})

case_with_differents_name_and_target = case_with_differents_name.copy()
case_with_differents_name_and_target.update({"target": [IDHolder(10)]})

case_with_differents_name_and_act_and_target = (
	case_with_differents_name_and_target.copy())
case_with_differents_name_and_act_and_target.update({"act": [IDHolder(45)]})

case_with_differents_all_comparable_attrs = (
	case_with_differents_name_and_act_and_target.copy())
case_with_differents_all_comparable_attrs.update({"d_in": [IDHolder(23),
														   IDHolder(56)]})