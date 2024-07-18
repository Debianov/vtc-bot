"""
This module contains the logic for outputting user docs.
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
		embed = BotEmbed(title="Documentation")
		embed.add_field(
			name="Welcome to the vtc-bot documentation!",
			value="Use :keyboard:help <command> to get information about the "
				"command."
		)
		channel = self.get_destination()
		await channel.send(embed=embed)

	# async def send_cog_help(self, cog: commands.Cog) -> None: # bug???
	# 	embed = BotEmbed(title="Documentation")
	# 	embed.add_field(
	# 		name = "Description",
	# 		value = cog.description(self, description)
	# 	)

	async def send_group_help(self, group: commands.Group) -> None:
		embed = BotEmbed(title="Documentation")
		embed.add_field(
			name="Description",
			value=group.help if group.help else "Missing."
		)
		embed.add_field(
			name="Subcommands:",
			value=""
		)
		for command in group.commands:
			if command.help:
				field_value = f"{command.help[:80]} \
				{'' if len(command.help) < 80 else '...'}"
			else:
				field_value = "Missing."
			embed.add_field(
				name=f"{command.name}{'/' if command.aliases else ...}"
				f"{'/'.join(command.aliases)}",
				value=field_value,
			)
		channel = self.get_destination()
		await channel.send(embed=embed)

	async def send_command_help(self, command: commands.Command) -> None:
		embed = BotEmbed(title="Documentation")
		value: str = ""
		if command.name == "help":
			value = "The command returns this message."
		else:
			value = command.help if command.help else "Missing."
		embed.add_field(
			name="Description",
			value=value,
		)
		channel = self.get_destination()
		await channel.send(embed=embed)

	async def send_error_message(self, error: str) -> None:
		embed = BotEmbed(title="Documentation")
		embed.add_field(
			name="Error",
			value="The command wasn't found."
		)
		channel = self.get_destination()
		await channel.send(embed=embed)