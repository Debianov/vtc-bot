import pytest
import discord.ext.test as dpytest

import bot.commands as user_commands

@pytest.mark.asyncio
async def test_bad_subcommand(botInit) -> None:
	pass

@pytest.mark.asyncio
async def test_good_log(botInit) -> None:
	await dpytest.message("sudo log 1 336420570449051649 asd 748764926897553450 -name ghds")
	assert dpytest.verify().message().content("Prikol")

@pytest.mark.asyncio
async def test_bad_log(botInit) -> None:
	pass

# # TODO вычисляем популярные команды и вставляет в тест сюда. Все команды в
# # одном файле здесь проверять смысла нет, поскольку для методов, которые
# # задействуются при вызове команд будут проверяться в отдельных модулях.
# @pytest.mark.asyncio
# async def test_on_message_with_popular_commands() -> None:
# 	pass