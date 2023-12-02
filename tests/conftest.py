import asyncio
import pathlib
import sys
from typing import AsyncGenerator, Generator, Tuple, Dict, Any
from bot.utils import Case
import discord
import discord.ext.test as dpytest
import pytest
import pytest_asyncio
from discord.ext import commands

root = pathlib.Path.cwd()

sys.path.append(str(root))

from bot.help import BotHelpCommand  # flake8: noqa: I005
from bot.main import BotConstructor  # flake8: noqa: I005
from bot.utils import DelayedExpressionEvaluator

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
	pytest.mark.doDelayedExpression = "is code below"
	if pyfuncitem.get_closest_marker("doDelayedExpression"):
		params_from_func = pyfuncitem.callspec.params
		params_and_fixtures = pyfuncitem.funcargs
		params_with_case = filterParametersWithCase(params_from_func)
		fixtures = filterFixtures(params_and_fixtures)
		for case in params_with_case.values():
			params_with_delayed_expr = case.getDelayedExprs()
			params_with_undelayed_expr: Dict[str, Any] = {}
			for (param, its_delay_exp) in params_with_delayed_expr:
				eval_results = DelayedExpressionEvaluator(
					list(its_delay_exp),
					fixtures).eval()
				params_with_undelayed_expr[param] = eval_results
			case.setUndelayedExprs(params_with_undelayed_expr)
