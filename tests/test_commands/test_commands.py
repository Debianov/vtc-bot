import asyncio
from typing import Any, Dict, Callable

import discord
import discord.ext.test as dpytest
import psycopg
import pytest
from discord.ext import commands

from bot.embeds import ErrorEmbed, SuccessEmbed
from bot.exceptions import DuplicateInstanceError
from bot.utils import Case, MockLocator, getDiscordMemberID

from .bad_cases import (  # empty_case
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
	case_with_all_channels_and_users_exprs,
	case_with_all_channels_exprs,
	case_with_all_users_exprs,
	compared_objects_for_all_channels_and_users_exprs,
	compared_objects_for_all_channels_exprs,
	compared_objects_for_all_users_exprs,
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
	await dpytest.message(case.getMessageStringWith("log 1",
		getDiscordMemberID))
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM log_targets;"
		)
		for row in await acur.fetchall():
			assert row == (str(mockLocator.guild.id),
				case["target"], case["act"], case["d_in"],
				*list(case["flags"].values()))

@pytest.mark.asyncio
async def test_good_log_create_without_flags(
	db: psycopg.AsyncConnection[Any],
	mockLocator: MockLocator
) -> None:
	parts = []
	parts.append("log 1")
	parts.append(str(mockLocator.members[0].id))
	parts.append("23")
	parts.append(str(mockLocator.members[1].id))
	await dpytest.message(" ".join(parts))
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM log_targets"
		)
		for row in await acur.fetchall():
			name, output, priority, other = (flag_values :=
											[None, None, None, None])
			assert row == (str(mockLocator.guild.id),
				[mockLocator.members[0]], '23', [mockLocator.members[1]],
				*flag_values)

@pytest.mark.asyncio
async def test_log_without_subcommand() -> None:
	await dpytest.message("log")
	assert dpytest.verify().message().content(
		"Убедитесь, что вы указали подкоманду.")

@pytest.mark.doDelayedExpression
@pytest.mark.parametrize(
	"case, missing_params",
	[
		(case_without_two_required_params, "act"),
		(case_without_one_required_params, "d_in"),
	]
)
@pytest.mark.asyncio
async def test_log_without_require_params(
	case: Case,
	missing_params: str
) -> None:
	with pytest.raises(commands.MissingRequiredArgument):
		await dpytest.message(case.getMessageStringWith("log 1"))
	assert dpytest.verify().message().content(f"Убедитесь, что вы указали "
		f"все обязательные параметры. Не найденный параметр: "
		f"{missing_params}")

@pytest.mark.asyncio
async def test_log_1_with_mention(mockLocator: MockLocator) -> None:
	await dpytest.message(f"log 1 <@{mockLocator.members[0].id}> 23"
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
		"log 1"))
	dpytest.get_message()

	await dpytest.message(compared_case.getMessageStringWith(
		"log 1"))
	bot_reply = dpytest.get_message().content
	coincidence_error_message_part = (f"({error_part['name']}). "
		f"Совпадающие элементы: "
		f"{', '.join(map(str, error_part['coincidence_elems']))}")
	assert coincidence_error_message_part in bot_reply

@pytest.mark.doDelayedExpression
@pytest.mark.parametrize(
	"case, compared_objects",
	[
		(
			case_with_all_users_exprs, compared_objects_for_all_users_exprs
		),
		(
			case_with_all_channels_and_users_exprs,
			compared_objects_for_all_channels_and_users_exprs
		),
		(
			case_with_all_channels_exprs, compared_objects_for_all_channels_exprs
		)
	]
)
@pytest.mark.asyncio
async def test_log_1_good_expression(
	db: psycopg.AsyncConnection[Any],
	case: Case,
	compared_objects: Case,
	mockLocator: MockLocator,
) -> None:
	await dpytest.message(f"log 1 {case['target']} 23"
		f" {case['d_in']}")
	assert dpytest.verify().message().content("Цель добавлена успешно.")
	async with db.cursor() as acur:
		await acur.execute(
			"SELECT * FROM log_targets"
		)
		for row in await acur.fetchall():
			name, output, priority, other = (flag_values :=
											[None, None, None, None])
			assert row == (str(mockLocator.guild.id),
				compared_objects["target"], '23', compared_objects["d_in"],
				*flag_values)

@pytest.mark.parametrize(
	"exp1, exp2, missing_params",
	[
		(
			"usr:*", "*df", "d_in"
		)
	]
)
@pytest.mark.asyncio
async def test_log_1_bad_expression(
	exp1: str,
	exp2: str,
	missing_params: str
) -> None:
	with pytest.raises(commands.CommandError):
		await dpytest.message(f"log 1 {exp1} 23"
			f" {exp2}")
	assert dpytest.verify().message().content(f"Убедитесь, что вы указали все"
		f" обязательные параметры. Не найденный параметр: {missing_params}")

@pytest.mark.parametrize(
	"language",
	["en", "english", "ru", "russian"]
)
@pytest.mark.asyncio
async def test_good_set_language(
	db: psycopg.AsyncConnection[Any],
	language: str
) -> None:
	await dpytest.message(f"setup lang {language}")
	reply_message = dpytest.get_message()
	if language == "en" or language == "english":
		en_reply_embed = SuccessEmbed().add_field(name="Success!",
		value="Bot language set.")
		assert reply_message.embeds[0] == en_reply_embed
	else:
		ru_reply_embed = SuccessEmbed().add_field(name="Успешно!",
		value="Язык бота установлен.")
		assert reply_message.embeds[0] == ru_reply_embed
	assert len(reply_message.embeds) <= 1
	await checkLanguageRecordInDB(db, language, reply_message)
	await checkLanguageSwitchingBetweenRuAndEn(language)
	await setEnglish()

async def checkLanguageRecordInDB(
	db: psycopg.AsyncConnection[Any],
	language: str,
	reply_message: discord.Message
):
	async with (db.cursor() as acur):
		await acur.execute("SELECT * FROM guilds")
		row_count = 0
		for row in await acur.fetchall():
			row_count += 1
			if reply_message.guild:
				assert row[:1] == (str(reply_message.guild.id),)
			elif reply_message.author.id:
				raise NotImplementedError
			if len(language) == 2:
				assert row[1].getFullName()
				assert row[1].getShortName() == language
			else:
				assert row[1].getShortName()
				assert row[1].getFullName() == language
		assert row_count <= 1, DuplicateInstanceError

async def checkLanguageSwitchingBetweenRuAndEn(language: str):
	await dpytest.message("setup")
	reply_message = dpytest.get_message()
	assert len(reply_message.embeds) <= 1
	if language in ["ru", "russian"]:
		ru_reply_embed = ErrorEmbed().add_field(name="Ошибка!",
		value="Эта команда может использоваться только с подкомандами.")
		assert reply_message.embeds[0] == ru_reply_embed
	elif language in ["en", "english"]:
		en_reply_embed = ErrorEmbed().add_field(name="Error!",
		value="This command can only be used with a subcommand.")
		assert reply_message.embeds[0] == en_reply_embed

async def setEnglish():
	await dpytest.message("setup lang en")
	reply_message = dpytest.get_message()
	en_reply_embed = SuccessEmbed().add_field(name="Success!",
		value="Bot language set.")
	assert reply_message.embeds[0] == en_reply_embed

@pytest.mark.parametrize(
	"language",
	["af", "hfghfgh"]
)
@pytest.mark.asyncio
async def test_bad_set_language(
	language: str
) -> None:
	with pytest.raises(commands.errors.CommandInvokeError):
		await dpytest.message(f"setup lang {language}")
	reply_message = dpytest.get_message()
	reply_embed = ErrorEmbed().add_field(name="Error!",
	value=f"{language}: the language isn't supported.")
	assert len(reply_message.embeds) <= 1
	assert reply_message.embeds[0] == reply_embed

@pytest.mark.asyncio
async def test_create_convoy() -> None:
	await dpytest.message('convoy create Belgrade Warsawa 01.08.24 12:00 (MSK) -rest Метка 1 '
								 '-map Baltic+Iberia+Южный Регион v12.2 -cargo Локомотив Vossloh G6 -extra_info RP-'
								 'режим через вкладку "Конвой" в ETS (отдельный сервер).')
	reply_message = dpytest.get_message()
	reply_embed = SuccessEmbed(title="Convoy").add_field(name="Description", value="Location: "
	"Belgrade\nDestination: Warsawa\nTime: 01.08.24 12:00 (MSK)")
	reply_embed = reply_embed.add_field(name="Information", value="Rest: Метка 1\nDLC maps: Baltic+Iberia+Южный регион "
	"v12.2\nCargo: Локомотив Vossloh G6")
	reply_embed.add_field(name="Extra information", value='RP-режим через вкладку "Конвой" в '
	'ETS (отдельный сервер).')
	assert reply_message.embeds[0] == reply_embed
	assert len(reply_message.embeds) <= 1, IndexError

def check_at_positive_vote_result(reply_message: discord.Message, reply_embed: discord.Embed) -> None:
	reply_embed_with_vote_result = reply_embed.add_field(name="Vote result",
	value="The vote is over. Convoy accepted.")
	assert reply_message.embeds[0] == reply_embed_with_vote_result


def check_at_negative_vote_result(reply_message: discord.Message, reply_embed: discord.Embed) -> None:
	reply_embed_with_vote_result = reply_embed.add_field(name="Vote result",
	value="The vote is over. Convoy rejected.")
	assert reply_message.embeds[0] == reply_embed_with_vote_result


def check_at_neutral_vote_result(reply_message: discord.Message, reply_embed: discord.Embed) -> None:
	reply_embed_with_vote_result = reply_embed.add_field(name="Vote result",
	value="The vote is over. Convoy rejected due to neutral vote.")
	assert reply_message.embeds[0] == reply_embed_with_vote_result

@pytest.mark.parametrize(
	"reaction, check_func",
	[
		(":white_check_mark:", check_at_positive_vote_result),
		(":x:", check_at_negative_vote_result),
		(":five:", check_at_neutral_vote_result)
	]
)
@pytest.mark.asyncio
async def test_create_convoy_with_vote(
		discordContext: commands.Context,
		reaction: str,
		check_func: Callable[[discord.Message, discord.Embed], None]
) -> None:
	await dpytest.message('convoy create Belgrade Warsawa 01.08.24 12:00 (MSK)'
	' -rest Метка 1 -map Baltic+Iberia+Южный Регион v12.2 -cargo Локомотив'
	' Vossloh G6 -extra_info RP-режим через вкладку "Конвой" в ETS (отдельный'
	' сервер). -vote 2s')
	reply_message = dpytest.get_message()
	reply_embed = SuccessEmbed(title="Convoy vote").add_field(name="Description",
	value="Location: Belgrade\nDestination: Warsawa\nTime: 01.08.24 12:00 (MSK)")
	reply_embed = reply_embed.add_field(name="Information",
	value="Rest: Метка 1\nDLC maps: Baltic+Iberia+Южный регион v12.2\nCargo: "
		"Локомотив Vossloh G6")
	reply_embed = reply_embed.add_field(name="Extra information",
	value='RP-режим через вкладку "Конвой" в ETS (отдельный сервер).')
	reply_embed_with_vote_info = reply_embed.add_field(name="Vote information",
	value="Vote within 5m.\nDo you accept with the convoy? :white_check_mark: "
		"- yes, :x: - no")
	assert reply_message.embeds[0] == reply_embed_with_vote_info
	assert len(reply_message.embeds) <= 1, IndexError
	await dpytest.add_reaction(reply_message, reaction)
	await asyncio.sleep(3)
	reply_message = await discordContext.fetch_message(reply_message.id)
	check_func(reply_message, reply_embed)

async def test_create_convoy_without_required_params():
	pass