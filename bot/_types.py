"""
This module contains the abstract classes.
"""

from typing import Protocol, Union, TypedDict

from discord import Member
from discord.abc import GuildChannel


class IDObjects(Protocol):
	
	id: int

DiscordGuildObjects = Union[GuildChannel, Member]

msgId = str