import discord
import logging
from bot.commands import bot, initDB

from typing import Optional, Union, Tuple

def runForPoetry() -> None:
	with open("dsAPI_secret.sec") as text:
		bot.run(text.readline())

async def setup_hook() -> None:
	with open("db_secret.sec") as text:
		await initDB(text.readline(), text.readline())
bot.setup_hook = setup_hook

if __name__ == "__main__":
	runForPoetry()