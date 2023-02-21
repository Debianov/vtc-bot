import pytest
from discord import MockMessage, MockChannel, response_to_test_messages
# кастомный discord.py. Опубликую изменённую библиотеку, либо модуль pytest
# (пока не изучал тех. возможность реализовать в виде модуля pytest).

import bot.main as bot

@pytest.mark.asyncio
async def test_on_message_without_command() -> None:
	message_instance = MockMessage(MockChannel(), "Привет, бот!")
	await bot.on_message(message_instance)
	assert response_to_test_messages.pop() == ""

# TODO вычисляем популярные команды и вставляет в тест сюда. Все команды в
# одном файле здесь проверять смысла нет, поскольку для методов, которые
# задействуются при вызове команд будут проверяться в отдельных модулях.
@pytest.mark.asyncio
async def test_on_message_with_popular_commands() -> None:
	pass