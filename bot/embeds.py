"""
Модуль содержит переопределённый embeds с некоторыми предустановками.
"""

import discord
from typing import Any

class BotEmbed(discord.Embed):
	
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		super().__init__(*args, **kwargs)
		self.set_footer(text="VCS discord bot", icon_url="https://sun9-61.userapi.com/impg/c85"
			"7324/v857324765/1d6cab/7CK2_ivIpls.jpg?size=303x391&quality=96&sign=bf7c5933c4064672c8"
			"69a41400f46118&type=album")
		self.colour = discord.Colour(12).green()