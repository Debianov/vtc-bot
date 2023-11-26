"""
Модуль предназначен для абстрактных классов.
"""

from typing import Protocol, Union

from discord import Member
from discord.abc import GuildChannel


class IDObjects(Protocol):
	
	id: int

DiscordGuildObjects = Union[GuildChannel, Member]


