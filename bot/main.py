import discord # TODO отсутствуют stubs-ы.
import logging
from bot.commands import bot

from typing import Optional, Union, Tuple

discord.utils.setup_logging(level=logging.DEBUG)

def runForPoetry() -> None:
	with open("secret.sec") as text:
		bot.run(text.readline())

if __name__ == "__main__":
	runForPoetry()