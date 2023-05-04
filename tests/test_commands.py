import pytest
import psycopg
import discord.ext.test as dpytest
import discord
from discord.ext import commands
from typing import List, Union, Optional, Dict, Tuple, Iterable, Sequence, Any

import bot.commands as user_commands

@pytest.mark.parametrize(
	"target, act, d_in, flags",
	[
		(
			['pytest.test_member0'],
			"23",
			['pytest.test_member1'],
			{"-name": "Test", "-output": "", "-priority": "-1", "other": ""}
		),
		(	
			['pytest.test_member0', 'pytest.test_member1'],
			"23",
			['pytest.test_member2', 'pytest.test_member3'],
			{"-name": "Test", "-output": "", "-priority": "-1", "other": ""}
		),
		(
			['pytest.test_member0'],
			"23",
			['pytest.test_member1'],
			{"-name": "Aboba", "-output": "", "-priority": "-1", "other": ""}
		),
	],
)
@pytest.mark.asyncio
async def test_good_log_create(
	bot: commands.Bot,
	db: Optional[psycopg.AsyncConnection[Any]],
	target: List[Optional[str]],
	act: str, 
	d_in: List[Optional[str]],
	flags: Dict[str, str]
	) -> None:
	target_message_part = extractIDAndGenerateObject(target)
	d_in_message_part = extractIDAndGenerateObject(d_in)
	joint_flags: Iterable[str] = filter(lambda x: False if not bool(x[1]) else x, flags.items())
	joint_flags = list(map(lambda x: " ".join(list(x)), joint_flags))
	await dpytest.message(f"sudo log 1 {' '.join(target_message_part)} {act} {' '.join(d_in_message_part)}"
	f" {' '.join(joint_flags)}")
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		for row in await acur.fetchall():
			flags_values = list(map(lambda x: None if not x else x, flags.values()))
			assert row == ("0", str(pytest.test_guild.id), target, act, d_in, *flags_values)

# @pytest.mark.asyncio
# async def test_bad_log(botInit) -> None:
# 	pass

def extractIDAndGenerateObject(sequence: List[Optional[str]]) -> Iterable[str]:
	message_part: List[Optional[str]] = []
	for (ind, string) in enumerate(sequence):
		try:
			discord_object = eval(string)
			sequence[ind] = discord_object
			message_part.append(str(discord_object.id))
		except Exception:
			continue
	return message_part if message_part else sequence

# # TODO вычисляем популярные команды и вставляет в тест сюда. Все команды в
# # одном файле здесь проверять смысла нет, поскольку для методов, которые
# # задействуются при вызове команд будут проверяться в отдельных модулях.
# @pytest.mark.asyncio
# async def test_on_message_with_popular_commands() -> None:
# 	pass