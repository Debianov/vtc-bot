"""
Модуль содержит логику для обработки и вывода пользовательской документации
"""

from typing import List, Mapping, Optional

from discord.ext import commands

from .embeds import BotEmbed


class BotHelpCommand(commands.HelpCommand):

	async def send_bot_help(
		self,
		mapping: Mapping[Optional[commands.Cog],
		List[commands.Command]]
	) -> None:
		embed = BotEmbed(title="Документация")
		embed.add_field(
			name="Добро пожаловать в документацию бота!",
			value="Введите конкретную команду, чтобы получить справку:\n"
			" :keyboard:help <название команды>"
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
			value=group.help if group.help else "Отсутствует."
		)
		embed.add_field(
			name="Подкоманды:",
			value=""
		)
		for command in group.commands:
			if command.help:
				field_value = f"{command.help[:80]} \
				{'' if len(command.help) < 80 else '...'}"
			else:
				field_value = "Описание отсутствует."
			embed.add_field(
				name=f"{command.name}{'/' if command.aliases else ...}"
				f"{'/'.join(command.aliases)}",
				value=field_value,
			)
		channel = self.get_destination()
		await channel.send(embed=embed)

	async def send_command_help(self, command: commands.Command) -> None:
		embed = BotEmbed(title="Документация")
		value: str = ""
		if command.name == "help":
			value = "Вывод данного сообщения."
		else:
			value = command.help if command.help else "Отсутствует."
		embed.add_field(
			name="Описание",
			value=value,
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