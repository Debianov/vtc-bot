
import discord.ext.test as dpytest
import pytest
from discord.ext import commands

from bot.converters import ShortSearchExpression
from bot.data import UserGroup
from bot.utils import MockLocator


@pytest.mark.asyncio
async def test_good_convertation(
	bot: commands.Bot,
	mockLocator: MockLocator
) -> None:
	a = ShortSearchExpression[UserGroup]
	message = await dpytest.message("sudo help")
	current_ctx = await bot.get_context(message)
	assert mockLocator.members == await a().convert(current_ctx, "*")