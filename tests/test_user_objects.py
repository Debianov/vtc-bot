import random
import pytest
import time
from typing import Final

from bot.objects.user_objects import UserAction, UserMessage, Guild, Content
from bot.objects.commands import UserLog, commands_collection
from bot.objects.exceptions import (DeterminingParameterError,
UnmatchingParameterTypeError, ActParameterError)

@pytest.mark.parametrize(
	"d_id, author, start_time", [
	(12423, pytest.MockMember, time.time()),
	(3424, pytest.MockMember, 12222)
])
def test_user_action_abstract_class(d_id, author, start_time) -> None:
	UserAction(d_id, author, start_time)

@pytest.mark.asyncio
async def test_user_message_without_command(getGoodGuildInstance) -> None:
	instance = UserMessage(13423, pytest.MockMember(), time.time(),
	getGoodGuildInstance, Content("rock"), pytest.MockChannel())
	await instance.reply()
	# TODO const
	assert pytest.response_to_test_messages.get_first_str() == "Не очень успешно!"
	assert instance.isCommand() is False

# TODO сделать, когда будут нормальные выводы команд log create.
# @pytest.mark.asyncio
# async def test_user_message_with_command() -> None:
# 	instance = UserMessage(13423, MockMember(), time.time(),
# 	getGoodGuildInstance(), Content(">sudo log 1 \"<@748764926897553450>\
# 	<@336420570449051649>\" -act 23 <@336420570449051649>"), MockChannel())
# 	await instance.reply()
# 	# assert response_to_test_messages.get_first_str() == "@748764926897553450 \
# 	# @336420570449051649 23 @336420570449051649      "
# 	assert instance.isCommand() is True

@pytest.mark.asyncio
async def test_user_message_reply(getGoodGuildInstance) -> None:
	instance = UserMessage(13423, pytest.MockMember(), time.time(),
	getGoodGuildInstance, Content(""), pytest.MockChannel())
	reply_message = "stat"
	await instance.reply_by_custome_text(reply_message)
	assert pytest.response_to_test_messages.get_first_str() == reply_message

@pytest.mark.parametrize(
	"global_prefix, access_prefix", [
		(pytest.global_prefix, pytest.access_prefix),
		(1234, 54234)
	]
)
def test_guild_class(global_prefix, access_prefix) -> None:
	instance = Guild(global_prefix, access_prefix)
	assert instance.getGlobalPrefix() == global_prefix
	assert instance.getAccessPrefix() == access_prefix

@pytest.mark.parametrize(
	"user_message, global_prefix, access_prefix", [
	(
		"{}{} log 1",
		">",
		"sudo"
	),
	(
		"{}{} log 1",
		">",
		""
	),
	(
		"{}{} log 1",
		"",
		"sudo"
	)
	]
)
def test_prefixes_parse(user_message, global_prefix, access_prefix,
getGoodGuildInstance) -> None:
	guild = getGoodGuildInstance
	instance = Content(user_message.format(pytest.global_prefix, pytest.access_prefix))
	instance.extractGlobalPrefix(guild)
	instance.extractAccessPrefix(guild)
	assert instance.getGlobalPrefix() == pytest.global_prefix
	assert instance.getAccessPrefix() == pytest.access_prefix
	instance.extractCommand(commands_collection)
	assert instance.getCommand() is UserLog.create

@pytest.mark.parametrize(
	"user_message, expect_parameters_dict", [
		# дефолтный вариант.
		(
			"{}{} log 1 <@748764926897553450> -act 23 <@336420570449051649>".format(
			pytest.global_prefix,
			pytest.access_prefix
		),
		{'target': '@748764926897553450', 'act': '23', 'd_in': '@336420570449051649',
		'name': '', 'output': '', 'priority': '', 'other': ''}
		),
		# вариант с группирующими кавычками.
		(
			"{}{} log 1 \"<@748764926897553450>"
		" <@336420570449051649>\" -act 23 <@336420570449051649>".format(
			pytest.global_prefix,
			pytest.access_prefix
		),
		{'target': '@748764926897553450'
		' @336420570449051649', 'act': '23', 'd_in': '@336420570449051649',
		'name': '', 'output': '', 'priority': '', 'other': ''}
		),
		# вариант с группирующими кавычками, между которыми пробел (был баг такой
		# вроде. А когда набираешь упоминание сразу после какого-символа в DS
		# без пробела, тебе не предлагают варианты упоминания пользователей в выпол
		# зающем окне).
		(
			"{}{} log 1 \" <@748764926897553450>"
		" <@336420570449051649> \" -act 23 <@336420570449051649>".format(
			pytest.global_prefix,
			pytest.access_prefix
		),
		{'target': '@748764926897553450'
		' @336420570449051649', 'act': '23', 'd_in': '@336420570449051649',
		'name': '', 'output': '', 'priority': '', 'other': ''}
		),
	]
)
def test_good_content_parses(user_message, expect_parameters_dict, getGoodGuildInstance) -> None:
	guild = getGoodGuildInstance
	instance = Content(user_message)
	instance.extractGlobalPrefix(guild) # TODO при закоменчивании этих
	# двух строк всё обваливается.
	instance.extractAccessPrefix(guild)
	# assert instance.getGlobalPrefix() == global_prefix
	# assert instance.getAccessPrefix() == access_prefix
	instance.extractCommand(commands_collection)
	assert instance.getCommand() is UserLog.create
	instance.extractParameters()
	assert instance.getParameters() == expect_parameters_dict

# TODO проверка ActParametersError, как только дойду.
@pytest.mark.parametrize(
	"user_message, expect_cls", [
		# нету всех обязательных аргументов.
		(
			"{}{} log 1 23".format(
				pytest.global_prefix,
				pytest.access_prefix
			),
			DeterminingParameterError
		),
		# параметр не указан явно, поэтому будет приниматься не за тот тип.
		# 23 должен быть за act, но в итоге примется за необязательный аргумент
		# name.
		(
			"{}{} log 1 <@748764926897553450> 23 <@336420570449051649>".format(
				pytest.global_prefix,
				pytest.access_prefix
			),
			DeterminingParameterError
		),
		# неправильный тип: в act команды log 1 принимаются только числа.
		(
			"{}{} log 1 <@748764926897553450> -act <@336420570449051649>"
			" <@336420570449051649>".format(
				pytest.global_prefix,
				pytest.access_prefix
			),
			UnmatchingParameterTypeError
		)
	]
)
def test_bad_content_parses(user_message, expect_cls, getGoodGuildInstance) -> None:
	guild = getGoodGuildInstance
	instance = Content(user_message)
	instance.extractGlobalPrefix(guild) # TODO при закоменчивании этих
	# двух строк всё обваливается.
	instance.extractAccessPrefix(guild)
	instance.extractCommand(commands_collection)
	assert instance.getCommand() is UserLog.create
	with pytest.raises(expect_cls):
		instance.extractParameters()