from typing import Any, Union

import discord

from bot.utils import Case, DelayedExpression


def getDiscordMemberObject(arg: Any) -> Union[str, Any]:
	if isinstance(arg, discord.Member):
		return str(arg.id)
	return arg

case_without_two_required_params = Case(
	target=DelayedExpression('mockLocator.members[0].id'),
	act="",
	d_in=""
)

case_without_one_required_params = Case(
	target=DelayedExpression('mockLocator.members[0].id'),
	act="23",
	d_in=""
)

empty_case = Case(
	target="",
	act="",
	d_in=""
)

case_without_explicit_flag = Case(
	target=DelayedExpression("mockLocator.members[0].id"),
	act="54",
	d_in=DelayedExpression("mockLocator.members[1].id"),
	flags="barhatniy_tyagi"
)