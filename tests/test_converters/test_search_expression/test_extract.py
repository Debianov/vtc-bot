from typing import Any

import discord.ext.test as dpytest
import pytest
from discord.ext import commands

from bot.converters import SearchExpression
from bot.data import UserGroup
from bot.exceptions import SearchExpressionNotFound
from bot.utils import DiscordObjEvaluator, MockLocator, removeNesting

# @pytest.mark.asyncio
# async def test_good_extractDataGroup(
# 	bot: commands.Bot,
# 	discordContext: commands.Context
# ) -> None:
# 	a = SearchExpression()
# 	a._extractDataGroup()