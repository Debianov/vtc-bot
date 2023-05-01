import pytest
import discord.ext.test as dpytest
from discord.ext import commands
from typing import List, Union, Optional, Dict, Tuple

import bot.commands as user_commands

# @pytest.mark.asyncio
# async def test_bad_subcommand(botInit) -> None:
# 	pass

@pytest.mark.parametrize(
	"target_mask, act, d_in_mask, flags",
	[
		(
			[True],
			"23",
			[True],
			{"-name": "Test", "-output": "", "-priority": "-1", "other": ""},
		)
	],
)
@pytest.mark.asyncio
async def test_good_log_create(
	bot: commands.Bot,
	setupDB: 'Optional[psycopg.AsyncConnection[Any]]',
	target_mask: List[str],
	act: str, 
	d_in_mask: List[str],
	flags: Dict[str, str]
	) -> None:
	target = []
	d_in = []
	joint_flags: List[str] = []
	for (ind, flag) in enumerate(target_mask):
		if flag:
			target.append(getattr(bot, f"test_member{ind}"))
	for (ind, flag) in enumerate(d_in_mask):
		ind = ind + 2
		if flag:
			d_in.append(getattr(bot, f"test_member{ind}"))
	target_ids = " ".join(list(map(lambda x: str(x.id), target)))
	d_in_ids = " ".join(list(map(lambda x: str(x.id), d_in)))
	joint_flags = filter(lambda x: False if not bool(x[1]) else x, flags.items())
	joint_flags = list(map(lambda x: " ".join(list(x)), joint_flags))
	await dpytest.message(f"sudo log 1 {target_ids} {act} {d_in_ids} {' '.join(joint_flags)}", channel=bot.test_channel)
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with setupDB.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		for row in await acur.fetchall():
			flags_values = list(map(lambda x: None if not x else x, flags.values()))
			assert row == ("0", str(bot.test_guild.id), target, act, d_in, *flags_values)
		
# @pytest.mark.asyncio
# async def test_bad_log(botInit) -> None:
# 	pass

# # TODO вычисляем популярные команды и вставляет в тест сюда. Все команды в
# # одном файле здесь проверять смысла нет, поскольку для методов, которые
# # задействуются при вызове команд будут проверяться в отдельных модулях.
# @pytest.mark.asyncio
# async def test_on_message_with_popular_commands() -> None:
# 	pass