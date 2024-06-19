from typing import Any, Dict, List

import discord.ext.test as dpytest
import psycopg
import pytest
from discord.ext import commands

from bot.utils import Case, DiscordObjEvaluator, MockLocator, getDiscordMemberID

from .bad_cases import (
	case_without_explicit_flag,
	case_without_one_required_params,
	case_without_two_required_params
)
from .coincidence_cases import (
	case_for_coincidence_0_1,
	case_for_coincidence_0_2,
	case_for_coincidence_1_1,
	case_for_coincidence_1_2,
	case_for_coincidence_2_1,
	case_for_coincidence_2_2,
	case_for_coincidence_3_1,
	case_for_coincidence_3_2,
	case_for_coincidence_4_1,
	case_for_coincidence_4_2,
	case_for_coincidence_5_1,
	case_for_coincidence_5_2,
	error_fragments_0,
	error_fragments_1,
	error_fragments_2,
	error_fragments_3,
	error_fragments_4,
	error_fragments_5
)
from .good_cases import (
	default_case,
	default_case_with_other_target_name,
	default_case_with_several_users
)


@pytest.mark.parametrize(
	"case",
	[default_case, default_case_with_several_users,
	default_case_with_other_target_name]
)
@pytest.mark.doDelayedExpression
@pytest.mark.asyncio
async def test_good_log_create_with_flags(
	db: psycopg.AsyncConnection[Any],
	mockLocator: MockLocator,
	case: Case
) -> None:
	await dpytest.message(case.getMessageStringWith("sudo log 1", getDiscordMemberID))
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		for row in await acur.fetchall():
			assert row == ("0", str(mockLocator.guild.id),
				*case["target"], case["act"], *case["d_in"],
				*list(case["flags"].values()))

@pytest.mark.asyncio
async def test_good_log_create_without_flags(
	db: psycopg.AsyncConnection[Any],
	mockLocator: MockLocator
) -> None:
	parts = []
	parts.append("sudo log 1")
	parts.append(str(mockLocator.members[0].id))
	parts.append("23")
	parts.append(str(mockLocator.members[1].id))
	await dpytest.message(" ".join(parts))
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM target"
		)
		for row in await acur.fetchall():
			flags_values = [None, None, '-1', None]
			assert row == ("0", str(mockLocator.guild.id),
				[mockLocator.members[0]], '23', [mockLocator.members[1]],
				*flags_values)

@pytest.mark.asyncio
async def test_log_without_subcommand() -> None:
	await dpytest.message("sudo log")
	assert dpytest.verify().message().content(
		"Убедитесь, что вы указали подкоманду.")

@pytest.mark.doDelayedExpression
@pytest.mark.parametrize(
	"case, missing_params",
	[
		(case_without_two_required_params, "act"),
		(case_without_one_required_params, "d_in"),
	]
	#( # TODO доработать
	# [""],
	# "",
	# [""],
	# "target"
	# ),
)
@pytest.mark.asyncio
async def test_log_without_require_params(
	case: Case,
	missing_params: str
) -> None:
	with pytest.raises(commands.MissingRequiredArgument): # TODO dpytest
		# почему-то принудительно поднимает исключения, хотя они могут
		# обрабатываться в on_command_error и проч. ивентах.
		await dpytest.message(case.getMessageStringWith("sudo log 1"))
	assert dpytest.verify().message().content(f"Убедитесь, что вы указали "
		f"все обязательные параметры. Не найденный параметр: "
		f"{missing_params}")

@pytest.mark.doDelayedExpression
@pytest.mark.parametrize(
	"case, unhandle_message_part",
	[(case_without_explicit_flag, "barhatniy_tyagi")]
)
@pytest.mark.asyncio
async def test_log_bad_flag(
	case: Case,
	unhandle_message_part: str
) -> None:
	with pytest.raises(commands.CommandInvokeError):
		await dpytest.message(case.getMessageStringWith("sudo log 1"))
	assert dpytest.verify().message().content("Убедитесь, что вы "
		"указали флаги явно, либо указали корректные данные."
		f" Необработанная часть сообщения: {unhandle_message_part}")

@pytest.mark.asyncio
async def test_log_bad_parameters() -> None:
	with pytest.raises(commands.CommandInvokeError):
		incorrect_id = 1107606170375565372
		await dpytest.message("sudo log 1 336420570449051649 43 "
		f"{incorrect_id}")
	assert dpytest.verify().message().content("Убедитесь, что вы указали "
		"флаги явно, либо указали корректные данные. "
		"Необработанная часть сообщения: 1107606170375565372")

@pytest.mark.asyncio
async def test_log_1_with_mention(mockLocator: MockLocator) -> None:
	await dpytest.message(f"sudo log 1 <@{mockLocator.members[0].id}> 23"
		f" <@{mockLocator.members[1].id}>")
	assert dpytest.verify().message().content("Цель добавлена успешно.")

@pytest.mark.doDelayedExpression
@pytest.mark.parametrize(
	"case, compared_case, error_part",
	[
		(case_for_coincidence_0_1, case_for_coincidence_0_2,
		error_fragments_0),
		(case_for_coincidence_1_1, case_for_coincidence_1_2,
		error_fragments_1),
		(case_for_coincidence_2_1, case_for_coincidence_2_2,
		error_fragments_2),
		(case_for_coincidence_3_1, case_for_coincidence_3_2,
		error_fragments_3),
		(case_for_coincidence_4_1, case_for_coincidence_4_2,
		error_fragments_4),
		(case_for_coincidence_5_1, case_for_coincidence_5_2,
		error_fragments_5)
	],
)
@pytest.mark.asyncio
async def test_coincidence_targets(
	case: Case,
	compared_case: Case,
	error_part: Dict[str, Any]
) -> None:

	await dpytest.message(case.getMessageStringWith(
		"sudo log 1"))
	dpytest.get_message()

	await dpytest.message(compared_case.getMessageStringWith(
		"sudo log 1"))
	assert dpytest.verify().message().content(f"Цель с подобными "
		f"параметрами уже существует: {error_part["id"]} "
		f"({error_part["name"]}). Совпадающие элементы: {", ".join(
		map(str, error_part["coincidence_elems"]))}")

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