import pytest
from discord.ext import commands

from bot.converters import ShortSearchExpression
from bot.exceptions import ShortSearchExpressionNotFound


@pytest.mark.parametrize(
	"wildcard",
	[
		("*")
	]
)
@pytest.mark.asyncio
async def test_good(
	bot: commands.Bot,
	discordContext: commands.Context,
	wildcard: str
) -> None:
	a = ShortSearchExpression
	a().checkExpression(wildcard)

@pytest.mark.parametrize(
	"wildcard",
	[
		"+",
		"-",
		"/"
	]
)
@pytest.mark.asyncio
async def test_bad(
	bot: commands.Bot,
	discordContext: commands.Context,
	wildcard: str
) -> None:
	a = ShortSearchExpression
	with pytest.raises(ShortSearchExpressionNotFound):
		a().checkExpression(wildcard)