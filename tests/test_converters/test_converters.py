import pytest
from discord.ext import commands

import discord.ext.test as dpytest

from bot.converters import ShortSearchExpression
from bot.data import UserGroup

from bot.utils import MockLocator

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