"""
This module contains the abstract classes.
"""

from typing import Protocol, Union

from discord import Member
from discord.abc import GuildChannel


class IDObjects(Protocol):
	
	id: int

DiscordGuildObjects = Union[GuildChannel, Member]

msgId = str

OR = 0
AND = 1

operator = Union[OR, AND]