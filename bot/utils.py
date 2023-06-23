from typing import Optional

import discord

class ContextProvider:
	"""
	Класс-локатор для приёма и передачи контекста.
	"""

	def __init__(self) -> None:
		self.context: Optional[discord.Guild] = None

	def updateContext(self, context: discord.Guild) -> None:
		self.context = context

	def getContext(self) -> discord.Guild:
		return self.context