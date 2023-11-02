from typing import Any

import discord.ext.test as dpytest
import pytest
from discord.ext import commands

from bot.converters import Expression, SearchExpression, ShortSearchExpression
from bot.data import UserGroup
from bot.exceptions import SearchExpressionNotFound
from bot.utils import DiscordObjEvaluator, MockLocator, removeNesting


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
	argument: str
) -> None:
	a = Expression
	message = await dpytest.message("sudo help")
	current_ctx = await bot.get_context(message)
	with pytest.raises(NotImplementedError):
		assert mockLocator.members == await a().convert(current_ctx, argument)
	with pytest.raises(NotImplementedError):
		assert mockLocator.members == await a().checkExpression(argument)

@pytest.mark.parametrize(
	"argument, compare_data",
	[
		("usr:*", "mockLocator.guild.members"),
		("ch:*", "mockLocator.guild.channels"),
	]
)
@pytest.mark.asyncio
async def test_good_search_expression_class(
	bot: commands.Bot,
	mockLocator: MockLocator,
	argument: str,
	compare_data: Any,
	discordObjectEvaluator: DiscordObjEvaluator
) -> None:
	a = SearchExpression
	message = await dpytest.message("sudo help")
	current_ctx = await bot.get_context(message)
	compare_data = discordObjectEvaluator.extractObjects(
		[compare_data],
		current_ctx
	)
	assert removeNesting(compare_data) == await a().convert(current_ctx, argument)

@pytest.mark.parametrize(
	"argument",
	[
		"fdgewrwer:*", "usr:23424", "rwerwe:rtert34r", "242sdfs"
	]
)
@pytest.mark.asyncio
async def test_bad_search_expression_class(
	bot: commands.Bot,
	mockLocator: MockLocator,
	argument: str,
	discordObjectEvaluator: DiscordObjEvaluator
) -> None:
	a = SearchExpression
	message = await dpytest.message("sudo help")
	current_ctx = await bot.get_context(message)
	with pytest.raises(SearchExpressionNotFound):
		await a().convert(current_ctx, argument)

def test_data_group_assignment() -> None:
	a = ShortSearchExpression[UserGroup]
	assert a.data_group == UserGroup

@pytest.mark.asyncio
async def test_good_convertation(
	bot: commands.Bot,
	mockLocator: MockLocator
) -> None:
	a = ShortSearchExpression[UserGroup]
	message = await dpytest.message("sudo help")
	current_ctx = await bot.get_context(message)
	assert mockLocator.members == await a().convert(current_ctx, "*")