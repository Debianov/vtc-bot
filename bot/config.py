"""
Модуль хранит конфигурацию бота для подключения к Discord API.
"""
import discord
from discord.ext import commands

from .help import BotHelpCommand

intents = discord.Intents.all()

bot = commands.Bot(
	command_prefix="sudo ",
	intents=intents,
	help_command=BotHelpCommand()
)