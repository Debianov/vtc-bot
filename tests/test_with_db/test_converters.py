import pytest
from discord.ext import commands

import discord.ext.test as dpytest

from bot.converters import ShortSearchExpression
from bot.data import UserGroup

a = ShortSearchExpression[UserGroup]

def test_data_group_assignment() -> None:
	assert a.data_group == UserGroup

@pytest.mark.asyncio
async def test_good_convertation(
	bot: commands.Bot
) -> None:
	dpytest.message("Byte")
	current_ctx = await bot.get_context(dpytest.verify().message())
	a.convert(current_ctx, "*")
	print(a)