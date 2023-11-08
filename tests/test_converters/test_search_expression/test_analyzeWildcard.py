from typing import List, Union

import discord
import pytest
from discord.ext import commands

from bot.converters import SearchExpression
from bot.data import DiscordObjectsGroup


@pytest.mark.parametrize(
	"wild_card",
	[
		("usr:*"),
		("*"),
		("23432:*"),
	]
)
@pytest.mark.asyncio
async def test_good_analyzeWildcard_with_one_group(
	bot: commands.Bot,
	discordContext: commands.Context,
	wild_card: str
) -> None:
	a = SearchExpression()
	a.ctx = discordContext
	a.string = wild_card.split(":")
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