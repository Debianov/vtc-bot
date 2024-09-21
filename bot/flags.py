"""
This module contains `flag instances <https://discordpy.readthedocs.io/en/
stable/ext/commands/api.html?highlight=flagconverter#discord.ext.commands.
FlagConverter>`_ for constructing a command parser.
"""

from typing import Optional, Union

from discord.ext import commands

from bot.converters import TimeExpression

class UserLogFlags( # type: ignore
	commands.FlagConverter,
	prefix='-',
	delimiter=' '
):
	name: Optional[Union[str]]
	output: Optional[Union[str]]
	priority: Optional[int]
	other: Optional[Union[str]]

class CreatingConvoyFlags(
	commands.FlagConverter,
	prefix="-",
	delimiter=' '
):
	rest: Optional[str]
	map: Optional[str]
	cargo: Optional[str]
	extra_info: Optional[str]
	vote: Optional[TimeExpression]