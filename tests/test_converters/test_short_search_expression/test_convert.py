
import pytest
from discord.ext import commands

from bot.converters import ShortSearchExpression
from bot.data import ChannelGroup, DiscordObjectsGroup, UserGroup
from bot.exceptions import ShortSearchExpressionNotFound


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
	data_group
) -> None:
	a = ShortSearchExpression[data_group]
	assert await a().convert(discordContext, wildcard) == list(data_group(
		discordContext).extractData())

@pytest.mark.parametrize(
	"wildcard, data_group, expected_exception",
	[
		("*", DiscordObjectsGroup, NotImplementedError),
		("*", [ChannelGroup, UserGroup], TypeError),
		("+", ChannelGroup, ShortSearchExpressionNotFound),
		("-", UserGroup, ShortSearchExpressionNotFound)
	]
)
@pytest.mark.asyncio
async def test_bad(
	bot: commands.Bot,
	discordContext: commands.Context,
	wildcard: str,
	data_group,
	expected_exception: type[Exception]
) -> None:
	a = ShortSearchExpression[data_group]
	with pytest.raises(expected_exception):
		await a().convert(discordContext, wildcard)