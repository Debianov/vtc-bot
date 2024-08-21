
import pytest

from bot.converters import ShortSearchExpression
from bot.data import ChannelGroup, DiscordObjectGroup, UserGroup


@pytest.mark.parametrize(
	"data_group_class",
	[UserGroup, ChannelGroup, DiscordObjectGroup]
)
def test_good(data_group_class) -> None:
	a = ShortSearchExpression[data_group_class]
	assert a.data_group == data_group_class

def test_without_group_passing() -> None:
	ShortSearchExpression[ChannelGroup]
	without_item = ShortSearchExpression
	assert without_item.data_group == (last_assignment_class := # noqa: F841
		ChannelGroup)