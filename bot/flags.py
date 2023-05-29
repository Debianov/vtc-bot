"""
Модуль содержит объекты флагов для построения парсинга команд.
"""

from discord.ext import commands
from typing import Optional, Union

class UserLogFlags(commands.FlagConverter, prefix='-', delimiter=' '):
	name: Optional[Union[str]]
	output: Optional[Union[str]]
	priority: Optional[int] = -1
	other: Optional[Union[str]]