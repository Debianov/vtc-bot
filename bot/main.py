import discord # TODO отсутствуют stubs-ы.
import logging
from bot.commands import bot

from typing import Optional, Union, Tuple

def runForPoetry() -> None:
	with open("dsAPI_secret.sec") as text:
		bot.run(text.readline())

if __name__ == "__main__":
	runForPoetry()