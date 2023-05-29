"""
Модуль хранит конфигурацию бота для подключения к Discord API.
"""
import discord
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(
	command_prefix="sudo ",
	intents=intents
)