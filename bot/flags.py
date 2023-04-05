from discord.ext import commands
from typing import Optional, Union

class UserLogFlags(commands.FlagConverter, prefix='-', delimiter=' '):
	name: Optional[Union[int, str]]
	output: Optional[Union[int, str]]
	priority: Optional[int] = -1
	other: Optional[Union[int, str]]