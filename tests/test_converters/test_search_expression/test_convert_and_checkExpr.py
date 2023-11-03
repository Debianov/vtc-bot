from typing import Any

import discord.ext.test as dpytest
import pytest
from discord.ext import commands

from bot.converters import Expression, SearchExpression, ShortSearchExpression
from bot.data import UserGroup
from bot.exceptions import NoticeForDeveloper, SearchExpressionNotFound
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
	assert removeNesting(compare_data) == await a().convert(discordContext, argument)
	a().checkExpression(argument)

@pytest.mark.parametrize(
	"argument",
	[
		"fdgewrwer:*", "usr:23424", "rwerwe:rtert34r", "242sdfs"
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


@pytest.mark.asyncio
async def test_good_checkExpr_without_args(
	bot: commands.Bot,
) -> None:
	a = SearchExpression()
	with pytest.raises(NoticeForDeveloper) as excp:
		a.checkExpression()
	assert excp.value.notice == ("self.argument doesn't exist because the"
		" convert method wasn't called. Call convert or pass argument.")