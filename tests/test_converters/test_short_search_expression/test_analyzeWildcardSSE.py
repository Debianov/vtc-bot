

import pytest
from discord.ext import commands

from bot.converters import ShortSearchExpression
from bot.data import ChannelGroup, UserGroup


@pytest.mark.parametrize(
	"wildcard, compare_data_groups",
	[
		("*", UserGroup),
		("*", ChannelGroup),
	]
)
@pytest.mark.asyncio
async def test_good_analyzeWildcard_with_one_group(
	discordContext: commands.Context,
	wildcard: str,
	compare_data_groups
) -> None:
	a = ShortSearchExpression[compare_data_groups]()
	a.wildcard = wildcard
	a.result = []
	a.data_group_instance = compare_data_groups(discordContext)
	a._analyzeWildcard()
	assert a.result == list(compare_data_groups(discordContext).extractData())
