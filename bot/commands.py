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

@bot.group(aliases=["logs"], invoke_without_command=True)
async def log(ctx: commands.Context) -> None:
	await ctx.send("Убедитесь, что вы указали пункт меню.")

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