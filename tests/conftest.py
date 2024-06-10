import asyncio
import pathlib
import sys
from typing import Any, AsyncGenerator, Dict, Generator, Tuple, List

import discord
import discord.ext.test as dpytest
import pytest
import pytest_asyncio
from discord.ext import commands
from bot.utils import DelayedExpressionReplacer, DelayedExpression



root = pathlib.Path.cwd()

sys.path.append(str(root))

from bot.help import BotHelpCommand  # flake8: noqa: I005
from bot.main import BotConstructor  # flake8: noqa: I005
from bot.utils import Case, DelayedExprsEvaluator

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
	# @pytest.mark.doDelayedExpression implementation
	if pyfuncitem.get_closest_marker("doDelayedExpression"):
		params_from_func = pyfuncitem.callspec.params
		params_and_fixtures = pyfuncitem.funcargs
		params_with_case = filterParametersWithCase(params_from_func)
		fixtures = filterFixtures(params_and_fixtures, params_with_case)
		for _, maybe_case in params_with_case.items():
			if isinstance(maybe_case, Case):
				DelayedExpressionReplacer(
					maybe_case.all_elems,
					fixtures
				).go()
			elif isinstance(maybe_case, ErrorFragments):
				DelayedExpressionReplacer(ErrorFragments.all_elems,
										  fixtures)

def filterParametersWithCase(
	params_from_func: Dict[str, object]
) -> Dict[str, Case]:
	params_with_case: Dict[str, Case] = {}
	for (param, object) in params_from_func.items():
		if isinstance(object, Case):
			params_with_case[param] = object
	return params_with_case


def filterFixtures(
	params_and_fixtures: Dict[str, Any],
	params_with_case: Dict[str, Case]
) -> Dict[str, Any]:
	fixtures: Dict[str, Case] = params_and_fixtures.copy()
	for param_key in params_with_case.keys():
		fixtures.pop(param_key)
	return fixtures