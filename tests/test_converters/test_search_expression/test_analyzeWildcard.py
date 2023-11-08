from typing import List, Union

import discord
import pytest
from discord.ext import commands

from bot.converters import SearchExpression
from bot.data import DiscordObjectsGroup


@pytest.mark.parametrize(
	"wildcard",
	[
		("*")
	]
)
@pytest.mark.asyncio
async def test_good_analyzeWildcard_with_one_group(
	bot: commands.Bot,
	discordContext: commands.Context,
	wildcard: str
) -> None:
	a = SearchExpression()
	a.ctx = discordContext
	a.wildcard = wildcard
	a.data_groups = [
		instance(discordContext) for instance in DiscordObjectsGroup.__subclasses__()
	]
	a.result = []
	a._analyzeWildcard()
	result_to_compare: List[
		Union[discord.abc.GuildChannel, discord.abc.Member]
	] = []
	for data_group in a.data_groups:
		result_to_compare += data_group.extractData()
	assert a.result == result_to_compare