from typing import List, Type

import pytest
from discord.ext import commands

from bot.converters import ShortSearchExpression
from bot.data import ChannelGroup, DiscordObjectsGroup, UserGroup, TargetGroup
from bot.exceptions import SearchExpressionNotFound

@pytest.mark.parametrize(
	"data_group_class",
	[UserGroup, ChannelGroup, DiscordObjectsGroup]
)
def test_good(data_group_class: DiscordObjectsGroup) -> None:
	a = ShortSearchExpression[data_group_class]
	assert a.data_group == data_group_class

def test_without_group_passing() -> None:
	a = ShortSearchExpression[ChannelGroup]
	a = ShortSearchExpression
	assert a.data_group == (last_assignment_class := ChannelGroup)