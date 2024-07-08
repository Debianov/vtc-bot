from typing import Any, Union

import discord

from bot.utils import Case, DelayedExpression


def getDiscordMemberObject(arg: Any) -> Union[str, Any]:
	if isinstance(arg, discord.Member):
		return str(arg.id)
	return arg

default_case = Case(
	target=[DelayedExpression('mockLocator.members[0]')],
	act="23",
	d_in=[DelayedExpression('mockLocator.members[1]')],
	flags={"-name": "Test", "-output": None, "-priority": "-1", "other": None}
)

default_case_with_several_users = Case(
	target=[DelayedExpression('mockLocator.members[0]'),
	DelayedExpression('mockLocator.members[1]')],
	act="23",
	d_in=[DelayedExpression('mockLocator.members[2]'),
	DelayedExpression('mockLocator.members[3]')],
	flags={"-name": "Test", "-output": None, "-priority": "-1",
	"other": None}
)

default_case_with_other_target_name = Case(
	target=[DelayedExpression('mockLocator.members[0]')],
	act="23",
	d_in=[DelayedExpression('mockLocator.members[1]')],
	flags={"-name": "Aboba", "-output": None, "-priority": "-1", "other": None}
)

case_with_all_users_exprs = Case(
	target="usr:*",
	d_in="usr:*",
)

compared_objects_for_all_users_exprs = Case(
	target=DelayedExpression('list(mockLocator.guild.members)'),
	d_in=DelayedExpression('list(mockLocator.guild.members)'),
)

case_with_all_channels_and_users_exprs = Case(
	target="ch:*",
	d_in="usr:*"
)

compared_objects_for_all_channels_and_users_exprs = Case(
	target=DelayedExpression('list(mockLocator.guild.channels)'),
	d_in=DelayedExpression('list(mockLocator.guild.members)')
)

case_with_all_channels_exprs = Case(
	target="ch:*",
	d_in="ch:*",
)

compared_objects_for_all_channels_exprs = Case(
	target=DelayedExpression('list(mockLocator.guild.channels)'),
	d_in=DelayedExpression('list(mockLocator.guild.channels)'),
)
