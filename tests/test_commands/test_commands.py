from typing import Any, Dict, Iterable, List, Optional

import discord
import discord.ext.test as dpytest
import psycopg
import pytest
from discord.ext import commands


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
		)
	],
)
@pytest.mark.asyncio
async def test_good_log_create_with_flags(
	bot: commands.Bot,
	db: Optional[psycopg.AsyncConnection[Any]],
	target: List[Optional[str]],
	act: str,
	d_in: List[Optional[str]],
	flags: Dict[str, str]
) -> None:
	target_message_part = extractIDAndGenerateObject(target)
	d_in_message_part = extractIDAndGenerateObject(d_in)
	joint_flags: Iterable[str] = filter(
		lambda x: False if not bool(x[1]) else x, flags.items())
	joint_flags = list(map(lambda x: " ".join(list(x)), joint_flags))
	await dpytest.message(f"sudo log 1 {' '.join(target_message_part)} "
	f"{act} {' '.join(d_in_message_part)} {' '.join(joint_flags)}")
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		for row in await acur.fetchall():
			flags_values = list(map(lambda x: None if not x else x, flags.values()))
			assert row == ("0", str(pytest.test_guild.id),
				target, act, d_in, *flags_values)

@pytest.mark.asyncio
async def test_good_log_create_without_flags(db:
		Optional[psycopg.AsyncConnection[Any]]) -> None:
	await dpytest.message(f"sudo log 1 {pytest.test_member0.id} "
		f"23 {pytest.test_member1.id}")
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		for row in await acur.fetchall():
			flags_values = [None, None, '-1', None]
			assert row == ("0", str(pytest.test_guild.id),
				[pytest.test_member0], '23', [pytest.test_member1], *flags_values)

@pytest.mark.asyncio
async def test_log_without_subcommand() -> None:
	await dpytest.message("sudo log")
	assert dpytest.verify().message().content(
		"Убедитесь, что вы указали подкоманду.")

@pytest.mark.parametrize(
	"target, act, d_in, missing_params",
	[
		(
			['pytest.test_member0'],
			"",
			[""],
			"act"
		),
		(
			['pytest.test_member0'],
			"23",
			[""],
			"d_in"
		),
		(
			[""],
			"",
			[""],
			"target"
		),
	]
)
@pytest.mark.asyncio
async def test_log_without_require_params(
	target: List[Optional[str]],
	act: str,
	d_in: List[Optional[str]],
	missing_params: str
) -> None:
	target_message_part = extractIDAndGenerateObject(target)
	d_in_message_part = extractIDAndGenerateObject(d_in)
	with pytest.raises(commands.MissingRequiredArgument): #! dpytest почему-то
		# принудительно поднимает исключения, хотя они могут обрабатываться в
		# on_command_error и проч. ивентах.
		await dpytest.message(f"sudo log 1 {' '.join(target_message_part)} {act}"
			f" {' '.join(d_in_message_part)}")
	assert dpytest.verify().message().content(f"Убедитесь, что вы указали все "
		f"обязательные параметры. Не найденный параметр: {missing_params}")

@pytest.mark.parametrize(
	"target, act, d_in, flag, unhandle_message_part",
	[
		(
			['pytest.test_member0'],
			"54",
			['pytest.test_member1'],
			"barhatniy_tyagi",
			"barhatniy_tyagi"
		)
	]
)
@pytest.mark.asyncio
async def test_log_bad_flag(
	target: List[Optional[str]],
	act: str,
	d_in: List[Optional[str]],
	flag: str,
	unhandle_message_part: str
) -> None:
	target_message_part = extractIDAndGenerateObject(target)
	d_in_message_part = extractIDAndGenerateObject(d_in)
	with pytest.raises(commands.CommandInvokeError):
		await dpytest.message(f"sudo log 1 {' '.join(target_message_part)} 43"
			f" {' '.join(d_in_message_part)} {flag}")
	assert dpytest.verify().message().content("Убедитесь, что вы "
		"указали флаги явно, либо указали корректные данные."
		f" Необработанная часть сообщения: {unhandle_message_part}")

@pytest.mark.asyncio
async def test_log_bad_parameters() -> None:
	with pytest.raises(commands.CommandInvokeError):
		await dpytest.message("sudo log 1 336420570449051649 43 "
		"1107606170375565372")
	assert dpytest.verify().message().content("Убедитесь, что вы указали "
		"флаги явно, либо указали корректные данные. "
		"Необработанная часть сообщения: 1107606170375565372")

@pytest.mark.parametrize(
	"target, act, d_in, name, compared_target, compared_act, compared_d_in,"
	"compared_name",
	# compared — т.е те параметры, которые будем отправлять вторым сообщением.
	[
		(
			['pytest.test_member0'],
			"26",
			['pytest.test_member1'],
			"Aboba",

			['pytest.test_member0'],
			"26",
			['pytest.test_member1'],
			"Aboba"
		),
		(
			['pytest.test_member0'],
			"26",
			['pytest.test_member1'],
			"Aboba",

			['pytest.test_member2'],
			"26",
			['pytest.test_member1'],
			"Aboba"
		),
		(
			['pytest.test_member0', 'pytest.test_member1'],
			"26",
			['pytest.test_member2', 'pytest.test_member3'],
			"Aboba",

			['pytest.test_member0', 'pytest.test_member1'],
			"26",
			['pytest.test_member2'],
			"Aboba"
		),
		(
			['pytest.test_member0'],
			"26",
			['pytest.test_member1'],
			"Aboba",

			['pytest.test_member2'],
			"8",
			['pytest.test_member3'],
			"Aboba"
		),
		(
			['pytest.test_member0'],
			"26",
			['pytest.test_member1'],
			"Aboba",

			['pytest.test_member0'],
			"26",
			['pytest.test_member1'],
			"aboba",
		),
		(
			['pytest.test_member0'],
			"26",
			['pytest.test_member1'],
			"Aboba",

			['pytest.test_member0'],
			"26",
			['pytest.test_member1'],
			"",
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
	name: str,
	compared_target: List[Optional[str]],
	compared_act: str,
	compared_d_in: List[Optional[str]],
	compared_name: str
) -> None:
	target_message_part = extractIDAndGenerateObject(target)
	d_in_message_part = extractIDAndGenerateObject(d_in)
	await dpytest.message(f"sudo log 1 {' '.join(target_message_part)} "
		f"{act} {' '.join(d_in_message_part)} -name {name}")
	dpytest.get_message() # пропускаем ненужное сообщение
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		rows = await acur.fetchall()
		row = rows[0]
		target_id = row[0]
		target_name = row[5]
	compared_target_message_part = extractIDAndGenerateObject(compared_target)
	compared_d_in_message_part = extractIDAndGenerateObject(compared_d_in)
	await dpytest.message(f"sudo log 1 {' '.join(compared_target_message_part)} "
		f"{compared_act} {' '.join(compared_d_in_message_part)}"
		f" -name {compared_name}")
	coincidence_elements = []
	current_objects = []
	compared_objects = []
	# склеивание списков.
	for check_object in [target_message_part, act, d_in_message_part, name]:
		if isinstance(check_object, list):
			current_objects += check_object
		else:
			current_objects.append(check_object)
	# склеивание списков.
	for check_object in [compared_target_message_part, compared_act,
		compared_d_in_message_part, compared_name]:
		if isinstance(check_object, list):
			compared_objects += check_object
		else:
			compared_objects.append(check_object)
	for current_object in current_objects: # поиск совпадений.
		if current_object in compared_objects:
			coincidence_elements.append(current_object)
	assert dpytest.verify().message().content(f"Цель с подобными параметрами "
		f"уже существует: {target_id} "
		f"({target_name}). Совпадающие элементы: {', '.join(coincidence_elements)}")

@pytest.mark.asyncio
async def test_log_1_with_mention() -> None:
	await dpytest.message(f"sudo log 1 <@{pytest.test_member0.id}> 23"
		f" <@{pytest.test_member1.id}>")
	assert dpytest.verify().message().content("Цель добавлена успешно.")

@pytest.mark.parametrize(
	"exp1, exp2, calls_sequence",
	[
		(
			"usr:*", "usr:*", ['current_ctx.guild.members', 'current_ctx.guild.members']
		),
		(
			"ch:*", "usr:*", ['current_ctx.guild.channels', 'current_ctx.guild.members']
		),
		(
			"ch:*", "ch:*", ['current_ctx.guild.channels', 'current_ctx.guild.channels']
		)
	]
)
@pytest.mark.asyncio
async def test_log_1_good_expression(
	bot: commands.Bot,
	db: Optional[psycopg.AsyncConnection[Any]],
	exp1: str,
	exp2: str,
	calls_sequence: List[str]
) -> None:
	message = await dpytest.message(f"sudo log 1 {exp1} 23"
		f" {exp2}")
	current_ctx = await bot.get_context(message)
	compared_objects = extractObjects(calls_sequence, current_ctx)
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		for row in await acur.fetchall():
			flags_values = [None, None, '-1', None]
			assert row == ("0", str(pytest.test_guild.id), compared_objects[0],
				'23', compared_objects[1], *flags_values)

@pytest.mark.parametrize(
	"exp1, exp2, missing_params",
	[
		(
			"fger", "erert", "target",
		),
		(
			"usr:*", "*df", "d_in"
		)
	]
)
@pytest.mark.asyncio
async def test_log_1_bad_expression(
	bot: commands.Bot,
	db: Optional[psycopg.AsyncConnection[Any]],
	exp1: str,
	exp2: str,
	missing_params: str
) -> None:
	with pytest.raises(commands.CommandError):
		await dpytest.message(f"sudo log 1 {exp1} 23"
			f" {exp2}")
	assert dpytest.verify().message().content(f"Убедитесь, что вы указали все"
		f" обязательные параметры. Не найденный параметр: {missing_params}")

def extractIDAndGenerateObject(sequence: List[Optional[str]]) -> Iterable[str]:
	"""
	Существование функции обусловлено непреодолимым желанием разработчика
	иметь в записях под декоратором parametrize человеческие извлечения
	атрибутов. С пр-ом там имём всё довольно сложно, поскольку это
	происходит на этапе инициализации кода.
	"""
	message_part: List[Optional[str]] = []
	for (ind, string) in enumerate(sequence):
		try:
			discord_object = eval(string)
			sequence[ind] = discord_object
			message_part.append(str(discord_object.id))
		except Exception:
			continue
	return message_part if message_part else sequence

def extractObjects(
	calls_sequence: List[str],
	current_ctx: commands.Context
) -> List[List[discord.abc.Messageable]]:
	"""
	Существование функции обусловлено непреодолимым желанием разработчика иметь
	в записях под декоратором parametrize человеческие извлечения атрибутов.
	"""
	result: List[List[discord.abc.Messageable]] = []
	for call in calls_sequence:
		discord_objects = eval(call)
		result.append(list(discord_objects))
	return result