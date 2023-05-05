import pytest
import psycopg
import discord.ext.test as dpytest
import discord
from discord.ext import commands
from typing import List, Union, Optional, Dict, Tuple, Iterable, Sequence, Any, Sized

import bot.commands as user_commands

# TODO возврат при вызове без подкоманды, без явного указания флагов, 
# тест при указании пользователя вне гильдии/несуществующего.
# тест expression-ов.
# тест https://discord.com/channels/476793048756387850/757216070925811722/1103660030269603880
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

@pytest.mark.parametrize(
	"target, act, d_in, name",
	[
		(
			['pytest.test_member0'],
			"26",
			['pytest.test_member1'],
			"Aboba"
		)
	]
)
@pytest.mark.asyncio
async def test_coincidence_targets(
	bot: commands.Bot,
	db: Optional[psycopg.AsyncConnection[Any]],
	target: List[Optional[str]],
	act: str,
	d_in: List[Optional[str]],
	name: str
	) -> None:
	target_objects = target[:]
	d_in_objects = target[:]
	target_message_part = extractIDAndGenerateObject(target)
	d_in_message_part = extractIDAndGenerateObject(d_in)
	await dpytest.message(f"sudo log 1 {' '.join(target_message_part)} {act} {' '.join(d_in_message_part)} -name {name}")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		rows = await acur.fetchall()
		row = rows[0]
		target_id = row[0]
		target_name = row[5]
	attr_to_change = ['target_message_part', 'act', 'd_in_message_part', 'name']
	for (ind, part_to_change) in enumerate(attr_to_change):
		old_part_value = locals().get(part_to_change)
		if part_to_change in ["target_message_part", "d_in_message_part"]:
			locals().update({part_to_change: pytest.test_member2.id}) #! якорь: остаётся только eval.
		else:
			locals()[part_to_change] = "32"
		await dpytest.message(f"sudo log 1 {' '.join(target_message_part)} {act} {' '.join(d_in_message_part)} -name {name}")
		
		unchanged_attr = attr_to_change[:]
		unchanged_attr.remove(part_to_change)
		coincidence_elements: List[str] = []
		for attr in unchanged_attr:
			unchanged_attr_value = locals()[attr]
			if isinstance(unchanged_attr_value, list):
				coincidence_elements += unchanged_attr_value
			else:
				coincidence_elements.append(unchanged_attr_value)
		print(dpytest.get_message().content)
		print(f"Цель с подобными параметрами уже существует: {target_id}"
		f" ({target_name}). Совпадающие элементы: {', '.join(coincidence_elements)}")
		# assert dpytest.verify().message().content(f"Цель с подобными параметрами уже существует: {target_id}"
		# f" ({target_name}). Совпадающие элементы: {', '.join(coincidence_elements)}")
		locals()[part_to_change] = old_part_value
	# await dpytest.message(f"sudo log 1 {[pytest.test_member2.id]} {act} {[pytest.test_member5.id]} {name}")

def extractIDAndGenerateObject(sequence: List[Optional[str]]) -> Iterable[str]: # TODO посмотреть, что будет при list.
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