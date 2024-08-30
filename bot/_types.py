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

OR: int = 0
AND: int = 1

operator = Union[OR, AND] # type: ignore[valid-type]
