
import pytest
from discord.ext import commands

from bot.converters import Expression
from bot.utils import MockLocator


@pytest.mark.parametrize(
	"argument",
	[
		"*", "random", "usr:*"
	]
)
@pytest.mark.asyncio
async def test_main_expression_class(
	bot: commands.Bot,
	mockLocator: MockLocator,
	argument: str,
	discordContext: commands.Context
) -> None:
	a = Expression
	with pytest.raises(NotImplementedError):
		assert mockLocator.members == await a().convert(discordContext, argument)
	with pytest.raises(NotImplementedError):
		assert mockLocator.members == await a().checkExpression(argument)
