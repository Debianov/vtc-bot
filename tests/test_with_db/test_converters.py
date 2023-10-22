import pytest
from discord.ext import commands

import discord.ext.test as dpytest

from bot.converters import ShortSearchExpression
from bot.data import UserGroup

from bot.utils import MockLocator

a = ShortSearchExpression[UserGroup]

def test_data_group_assignment() -> None:
	assert a.data_group == UserGroup

@pytest.mark.asyncio
async def test_good_convertation(
	bot: commands.Bot,
	mockLocator: MockLocator
) -> None:
	message = await dpytest.message("sudo help")
	current_ctx = await bot.get_context(message)
	assert mockLocator.members == await a.convert(current_ctx, "*")