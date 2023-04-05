import discord
from discord.ext import commands
from typing import Optional, Union, Tuple

from .flags import *

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
	command_prefix="sudo ",
	intents=intents
)

def is_me():
	def checkSubcommandPresence(ctx) -> bool:
		# ctx.command.invoke_without_command #! это всё можно было бы сделать одной строкой, если бы данная штука работала.
		current_content = ctx.message.content
		current_content = current_content.removeprefix(ctx.prefix)
		base_content_len = len(current_content)
		current_main_command_aliases = list(ctx.command.aliases) + [ctx.command.name]
		for command_alias in current_main_command_aliases:
			current_content = current_content.removeprefix(command_alias + " ")
			if len(current_content) != base_content_len:
				break
		for command in ctx.command.commands:
			for alias in list(command.aliases) + [command.name]:
				if current_content.startswith(alias):
					return True
		return False
		# TODO вывод ошибки.
	return commands.check(checkSubcommandPresence)

@bot.group(aliases=["logs"])
@is_me()
async def log(ctx: commands.Context) -> None:
	pass

@log.command(aliases=["1", "cr"])
async def create(
	ctx: commands.Context,
	target: commands.Greedy[Union[discord.TextChannel, discord.Member]],
	act: Union[str, int],
	d_in: commands.Greedy[Union[discord.TextChannel, discord.Member]],
	*,
	flags: UserLogFlags
) -> None:
	pass