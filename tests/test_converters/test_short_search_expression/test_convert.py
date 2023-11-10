from typing import List, Type

import pytest
from discord.ext import commands

from bot.converters import ShortSearchExpression
from bot.data import ChannelGroup, DiscordObjectsGroup, UserGroup
from bot.exceptions import SearchExpressionNotFound

@pytest.mark.parametrize(
	"wildcard, data_group",
	[
		("*", ChannelGroup),
		("*", UserGroup)
	]
)
@pytest.mark.asyncio
async def test_good(
	bot: commands.Bot,
	discordContext: commands.Context,
	wildcard: str,
	data_group: DiscordObjectsGroup
) -> None:
	a = ShortSearchExpression[data_group]
	assert await a().convert(discordContext, wildcard) == list(data_group(discordContext).
		extractData())