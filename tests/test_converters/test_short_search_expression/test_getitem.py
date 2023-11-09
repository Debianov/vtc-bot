from typing import List, Type

import pytest
from discord.ext import commands

from bot.converters import ShortSearchExpression
from bot.data import ChannelGroup, DiscordObjectsGroup, UserGroup
from bot.exceptions import SearchExpressionNotFound

def test_good() -> None:
	a = ShortSearchExpression[UserGroup]
	assert a.data_group == UserGroup

def test_without_group_passing() -> None:
	a = ShortSearchExpression[ChannelGroup]
	a = ShortSearchExpression
	assert a.data_group == (last_assignment_class := ChannelGroup)