import asyncio
import pathlib
import sys
from typing import Any, AsyncGenerator, Dict, Generator, Tuple

import discord
import discord.ext.test as dpytest
import pytest
import pytest_asyncio
from discord.ext import commands

from bot.utils import Case

root = pathlib.Path.cwd()

sys.path.append(str(root))

from bot.help import BotHelpCommand  # flake8: noqa: I005
from bot.main import BotConstructor  # flake8: noqa: I005
from bot.utils import (
	DelayedExpressionEvaluator,
	evalAndWriteDelayedExprInParams,
	filterFixtures,
	filterParametersWithCase
)

# flake8: noqa: I005
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="package")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
	loop = asyncio.get_event_loop()
	yield loop
	loop.close()

@pytest_asyncio.fixture(autouse=True)
async def cleanUp() -> AsyncGenerator[None, None]:
	yield
	await dpytest.empty_queue()

def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> None:
		# @pytest.mark.doDelayedExpression
		if pyfuncitem.get_closest_marker("doDelayedExpression"):
			params_from_func = pyfuncitem.callspec.params
			params_and_fixtures = pyfuncitem.funcargs
			params_with_case = filterParametersWithCase(params_from_func)
			fixtures = filterFixtures(params_and_fixtures, params_with_case)
			evalAndWriteDelayedExprInParams(list(params_with_case.values()), fixtures)