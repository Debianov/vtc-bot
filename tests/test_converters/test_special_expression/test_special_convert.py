
import pytest
from discord.ext import commands

from bot.converters import SpecialExpression
from bot.exceptions import SpecialExpressionNotFound


@pytest.mark.parametrize(
	"argument",
	[
		"df", "default"
	]
)
@pytest.mark.asyncio
async def test_good(
	bot: commands.Bot,
	discordContext: commands.Context,
	argument: str,
) -> None:
	assert await SpecialExpression().convert(discordContext, argument) == argument

@pytest.mark.parametrize(
	"argument",
	[
		"dg", "qwe", "usr:*", "+"
	]
)
@pytest.mark.asyncio
async def test_bad(
	bot: commands.Bot,
	discordContext: commands.Context,
	argument: str,
) -> None:
	with pytest.raises(SpecialExpressionNotFound):
		await SpecialExpression().convert(discordContext, argument)