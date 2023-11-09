from typing import Any

import pytest
from discord.ext import commands

from bot.converters import SearchExpression
from bot.exceptions import SearchExpressionNotFound
from bot.utils import DiscordObjEvaluator, MockLocator, removeNesting


@pytest.mark.parametrize(
	"argument, compare_data",
	[
		("usr:*", "mockLocator.guild.members"),
		("ch:*", "mockLocator.guild.channels"),
	]
)
@pytest.mark.asyncio
async def test_good_search_expression_convert_and_checkExpr(
	bot: commands.Bot,
	mockLocator: MockLocator,
	argument: str,
	compare_data: Any,
	discordObjectEvaluator: DiscordObjEvaluator,
	discordContext: commands.Context
) -> None:
	a = SearchExpression
	compare_data = discordObjectEvaluator.extractObjects(
		[compare_data],
		discordContext
	)
	assert (removeNesting(compare_data) ==
		await a().convert(discordContext, argument))
	a().checkExpression(argument)

@pytest.mark.parametrize(
	"argument",
	[
		"fdgewrwer:*", "usr:23424", "rwerwe:rtert34r", "242sdfs",
		"usr: *", "ch   :*"
	]
)
@pytest.mark.asyncio
async def test_bad_search_expression_convert_and_checkExpr(
	bot: commands.Bot,
	mockLocator: MockLocator,
	argument: str,
	discordObjectEvaluator: DiscordObjEvaluator,
	discordContext: commands.Context
) -> None:
	a = SearchExpression
	with pytest.raises(SearchExpressionNotFound):
		await a().convert(discordContext, argument)
		a().checkExpression(argument)