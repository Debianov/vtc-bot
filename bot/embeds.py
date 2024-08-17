"""
This module contains overriding `embeds <https://discordpy.readthedocs.io/
en/stable/api.html?highlight=embed#discord.Embed>`_.
"""

from typing import Any, Self

import discord


class BaseEmbed(discord.Embed):

	def __init__(self, *args: Any, **kwargs: Any) -> None:
		super().__init__(*args, **kwargs)
		self.set_footer(text="vtc-bot project", icon_url="https://sun9-61.usera"
			"pi.com/impg/c857324/v857324765/1d6cab/7CK2_ivIpls.jpg?size=303x391&"
			"quality=96&sign=bf7c5933c4064672c8"
			"69a41400f46118&type=album")

	def add_field(
		self,
		*,
		name: str,
		value: str,
		inline: bool = False
	) -> Self:
		super().add_field(name=name, value=value, inline=inline)
		return self

class SuccessEmbed(BaseEmbed):

	def __init__(self, *args: Any, **kwargs: Any) -> None:
		self.colour = discord.Colour(12).green()
		super().__init__(*args, **kwargs)

class WarningEmbed(BaseEmbed):

	def __init__(self, *args: Any, **kwargs: Any) -> None:
		self.colour = discord.Colour(12).yellow()
		super().__init__(*args, **kwargs)

class ErrorEmbed(BaseEmbed):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		self.colour = discord.Colour(12).red()
		super().__init__(*args, **kwargs)