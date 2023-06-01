"""
Модуль содержит логику для обработки и вывода пользовательской документации
"""

from typing import Mapping, Optional, List
import discord
from discord.ext import commands
from .embeds import BotEmbed

class BotHelpCommand(commands.HelpCommand):

	async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]])\
	-> None:
		embed = BotEmbed(title="Документация")
		embed.add_field(
			name="Добро пожаловать в документацию бота!",
			value="Введите конкретную конкретную команду, чтобы получить справку:\n"
			" :keyboard:help <название команды>"
		)
		embed.add_field(
			name="Список команд представлен ниже.",
			value="",
		)
		commands = mapping.get(None)
		commands = await self.filter_commands(commands, sort=True)
		commands = filter(lambda x: x.name != "help", commands)
		for command_object in commands:
			embed.add_field(
				name=f"{command_object.name}{'/' if command_object.aliases else ...}{'/'.join(command_object.aliases)}",
				value=f"{command_object.help[:80]} {'' if len(command_object.help) < 80 else '...'}",
			)
		channel = self.get_destination()
		await channel.send(embed=embed)

	# async def send_cog_help(self, cog: commands.Cog) -> None: # когов:нет
	# 	embed = BotEmbed(title="Документация")
	# 	embed.add_field(
	# 		name = "Описание",
	# 		value = cog.description(self, description)
	# 	)

	async def send_group_help(self, group: commands.Group) -> None:
		embed = BotEmbed(title="Документация")
		embed.add_field(
			name="Описание",
			value=group.help
		)
		embed.add_field(
			name="Подкоманды:",
			value="",
			)
		for command in group.commands:
			embed.add_field(
				name=f"{command.name}{'/' if command.aliases else ...}{'/'.join(command.aliases)}",
				value=f"{command.help[:80]} {'' if len(command.help) < 80 else '...'}",
			)
		channel = self.get_destination()
		await channel.send(embed=embed)
		
	async def send_command_help(self, command: commands.Command) -> None:
		embed = BotEmbed(title="Документация")
		embed.add_field(
			name="Описание",
			value=command.help,
		)
		channel = self.get_destination()
		await channel.send(embed=embed)

	async def send_error_message(self, error: str) -> None:
		embed = BotEmbed(title="Документация")
		embed.add_field(
			name="Ошибка",
			value="Указанная команда не найдена."
		)
		channel = self.get_destination()
		await channel.send(embed=embed)