from typing import Any

import pytest
from discord.ext import commands

from bot.converters import SearchExpression
from bot.exceptions import SearchExpressionNotFound
from bot.utils import DelayedExpression, removeNesting


@pytest.mark.doDelayedExpression
@pytest.mark.parametrize(
	"argument, compare_data",
	[
		("usr:*", [DelayedExpression("list(mockLocator.guild.members)")]),
		("ch:*", [DelayedExpression("list(mockLocator.guild.channels)")]),
	]
)
@pytest.mark.asyncio
async def test_good_search_expression_convert_and_checkExpr(
	argument: str,
	compare_data: Any,
	discordContext: commands.Context
) -> None:
	a = SearchExpression
	assert (removeNesting(compare_data) == await a().convert(discordContext,
		argument))
	a()._checkExpression(argument)

@pytest.mark.parametrize(
	"argument",
	[
		"fdgewrwer:*", "usr:23424", "rwerwe:rtert34r", "242sdfs",
		"usr: *", "ch   :*"
	]
)
@pytest.mark.asyncio
async def test_bad_search_expression_convert_and_checkExpr(
	argument: str,
	discordContext: commands.Context
) -> None:
	a = SearchExpression
	with pytest.raises(SearchExpressionNotFound):
		await a().convert(discordContext, argument)
		a()._checkExpression(argument)