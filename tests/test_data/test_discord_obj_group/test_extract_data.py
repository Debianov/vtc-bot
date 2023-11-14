
from discord.ext import commands

from bot.data import ChannelGroup, UserGroup
from bot.utils import MockLocator


def test_user_group(
	discordContext: commands.Context,
	mockLocator: MockLocator
):
	a = UserGroup(discordContext)
	assert list(a.extractData()) == mockLocator.members

def test_channel_group(
	discordContext: commands.Context,
	mockLocator: MockLocator
):
	a = ChannelGroup(discordContext)
	assert list(a.extractData()) == list(mockLocator.guild.channels)
