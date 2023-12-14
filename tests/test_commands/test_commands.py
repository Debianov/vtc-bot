from typing import Any, Dict, Iterable, List

import discord.ext.test as dpytest
import psycopg
import pytest
from discord.ext import commands

from bot.utils import DiscordObjEvaluator, MockLocator, Case, DelayedExpressionEvaluator, DelayedExpression
from .good_cases import default_case, default_case_with_several_users, default_case_with_other_target_name

@pytest.mark.parametrize(
	"case",
	[default_case, default_case_with_several_users, default_case_with_other_target_name]
)

@pytest.mark.doDelayedExpression
@pytest.mark.asyncio
async def test_good_log_create_with_flags(
	db: psycopg.AsyncConnection[Any],
	# target: List[str],
	# act: str,
	# d_in: List[str],
	# flags: Dict[str, str],
	mockLocator: MockLocator,
	# discordObjectEvaluator: DiscordObjEvaluator
	case: Case
) -> None:
	joint_flags: Iterable[str] = filter(
		lambda x: False if not bool(x[1]) else x, # type: ignore [arg-type]
		case["flags"].items())
	joint_flags = list(map(lambda x: " ".join(list(x)), joint_flags))
	await dpytest.message(f"sudo log 1 {' '.join(case["target"])} "
	f"{case["act"]} {' '.join(case["d_in"])} {' '.join(joint_flags)}")
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		for row in await acur.fetchall():
			flags_values = list(map(lambda x: None if not x else x, case["flags"].values()))
			assert row == ("0", str(mockLocator.guild.id),
				case["target"], case["act"], case["d_in"], *flags_values)

@pytest.mark.asyncio
async def test_good_log_create_without_flags(
	db: psycopg.AsyncConnection[Any],
	mockLocator: MockLocator
) -> None:
	await dpytest.message(f"sudo log 1 {mockLocator.members[0].id} "
		f"23 {mockLocator.members[1].id}")
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		for row in await acur.fetchall():
			flags_values = [None, None, '-1', None]
			assert row == ("0", str(mockLocator.guild.id),
				[mockLocator.members[0]], '23', [mockLocator.members[1]], *flags_values)

@pytest.mark.asyncio
async def test_log_without_subcommand() -> None:
	await dpytest.message("sudo log")
	assert dpytest.verify().message().content(
		"Убедитесь, что вы указали подкоманду.")

@pytest.mark.parametrize(
	"target, act, d_in, missing_params",
	[
		(
			['mockLocator.members[0]'],
			"",
			[""],
			"act"
		),
		(
			['mockLocator.members[0]'],
			"23",
			[""],
			"d_in"
		),
		# ( # доработать
		# 	[""],
		# 	"",
		# 	[""],
		# 	"target"
		# ),
	]
)
@pytest.mark.asyncio
async def test_log_without_require_params(
	target: List[str],
	act: str,
	d_in: List[str],
	missing_params: str,
	discordObjectEvaluator: DiscordObjEvaluator
) -> None:
	target_message_part =\
		discordObjectEvaluator.extractIDAndGenerateObject(target)
	d_in_message_part =\
		discordObjectEvaluator.extractIDAndGenerateObject(d_in)
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
			['mockLocator.members[0]'],
			"54",
			['mockLocator.members[1]'],
			"barhatniy_tyagi",
			"barhatniy_tyagi"
		)
	]
)
@pytest.mark.asyncio
async def test_log_bad_flag(
	target: List[str],
	act: str,
	d_in: List[str],
	flag: str,
	unhandle_message_part: str,
	discordObjectEvaluator: DiscordObjEvaluator
) -> None:
	target_message_part =\
		discordObjectEvaluator.extractIDAndGenerateObject(target)
	d_in_message_part =\
		discordObjectEvaluator.extractIDAndGenerateObject(d_in)
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
			['mockLocator.members[0]'],
			"26",
			['mockLocator.members[1]'],
			"Aboba",

			['mockLocator.members[0]'],
			"26",
			['mockLocator.members[1]'],
			"Aboba"
		),
		(
			['mockLocator.members[0]'],
			"26",
			['mockLocator.members[1]'],
			"Aboba",

			['mockLocator.members[2]'],
			"26",
			['mockLocator.members[1]'],
			"Aboba"
		),
		(
			['mockLocator.members[0]', 'mockLocator.members[1]'],
			"26",
			['mockLocator.members[2]', 'mockLocator.members[3]'],
			"Aboba",

			['mockLocator.members[0]', 'mockLocator.members[1]'],
			"26",
			['mockLocator.members[2]'],
			"Aboba"
		),
		(
			['mockLocator.members[0]'],
			"26",
			['mockLocator.members[1]'],
			"Aboba",

			['mockLocator.members[2]'],
			"8",
			['mockLocator.members[3]'],
			"Aboba"
		),
		(
			['mockLocator.members[0]'],
			"26",
			['mockLocator.members[1]'],
			"Aboba",

			['mockLocator.members[0]'],
			"26",
			['mockLocator.members[1]'],
			"aboba",
		),
		(
			['mockLocator.members[0]'],
			"26",
			['mockLocator.members[1]'],
			"Aboba",

			['mockLocator.members[0]'],
			"26",
			['mockLocator.members[1]'],
			"",
		)
	]
)
@pytest.mark.asyncio
async def test_coincidence_targets(
	bot: commands.Bot,
	db: psycopg.AsyncConnection[Any],
	target: List[str],
	act: str,
	d_in: List[str],
	name: str,
	compared_target: List[str],
	compared_act: str,
	compared_d_in: List[str],
	compared_name: str,
	discordObjectEvaluator: DiscordObjEvaluator
) -> None:
	target_message_part =\
		discordObjectEvaluator.extractIDAndGenerateObject(target)
	d_in_message_part =\
		discordObjectEvaluator.extractIDAndGenerateObject(d_in)
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
	compared_target_message_part =\
		discordObjectEvaluator.extractIDAndGenerateObject(compared_target)
	compared_d_in_message_part =\
		discordObjectEvaluator.extractIDAndGenerateObject(compared_d_in)
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
async def test_log_1_with_mention(mockLocator: MockLocator) -> None:
	await dpytest.message(f"sudo log 1 <@{mockLocator.members[0].id}> 23"
		f" <@{mockLocator.members[1].id}>")
	assert dpytest.verify().message().content("Цель добавлена успешно.")

@pytest.mark.parametrize(
	"exp1, exp2, calls_sequence",
	[
		(
			"usr:*", "usr:*", ['mockLocator.guild.members', 'mockLocator.guild.members']
		),
		(
			"ch:*", "usr:*", ['mockLocator.guild.channels', 'mockLocator.guild.members']
		),
		(
			"ch:*", "ch:*", ['mockLocator.guild.channels', 'mockLocator.guild.channels']
		)
	]
)
@pytest.mark.asyncio
async def test_log_1_good_expression(
	bot: commands.Bot,
	db: psycopg.AsyncConnection[Any],
	exp1: str,
	exp2: str,
	calls_sequence: List[str],
	mockLocator: MockLocator,
	discordObjectEvaluator: DiscordObjEvaluator
) -> None:
	message = await dpytest.message(f"sudo log 1 {exp1} 23"
		f" {exp2}")
	current_ctx = await bot.get_context(message)
	compared_objects =\
		discordObjectEvaluator.extractObjects(calls_sequence, current_ctx)
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		for row in await acur.fetchall():
			flags_values = [None, None, '-1', None]
			assert row == ("0", str(mockLocator.guild.id), compared_objects[0],
				'23', compared_objects[1], *flags_values)

@pytest.mark.parametrize(
	"exp1, exp2, missing_params",
	[
		# ( # доработать
		# 	"fger", "erert", "target",
		# ),
		(
			"usr:*", "*df", "d_in"
		)
	]
)
@pytest.mark.asyncio
async def test_log_1_bad_expression(
	bot: commands.Bot,
	db: psycopg.AsyncConnection[Any],
	exp1: str,
	exp2: str,
	missing_params: str
) -> None:
	with pytest.raises(commands.CommandError):
		await dpytest.message(f"sudo log 1 {exp1} 23"
			f" {exp2}")
	assert dpytest.verify().message().content(f"Убедитесь, что вы указали все"
		f" обязательные параметры. Не найденный параметр: {missing_params}")