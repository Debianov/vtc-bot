import asyncio
import pathlib
import sys
from typing import Any, AsyncGenerator, Dict, Generator, Tuple, List

import discord
import discord.ext.test as dpytest
import pytest
import pytest_asyncio
from discord.ext import commands



root = pathlib.Path.cwd()

sys.path.append(str(root))

from bot.help import BotHelpCommand  # flake8: noqa: I005
from bot.main import BotConstructor  # flake8: noqa: I005
from bot.utils import Case, DelayedExpressionEvaluator

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


def evalAndWriteDelayedExprInParams(
	cases: List[Case],
	fixtures: Dict[str, Any]
) -> None:
	"""
	The func acts on Case directly via a reference.
	Args:
		cases(List[Case]): any `Case` instances that located in Dict with params
		as value (e.x `pytest.Function.callspec.params <https://docs.pytest.org/
		en/7.1.x/reference/reference.html#pytest.Function>`).
	"""
	for case in cases:
		params_with_delayed_expr = case.getDelayedExprs()
		params_with_undelayed_expr: Dict[str, Any] = {}
		for (param, its_delay_exp) in params_with_delayed_expr.items():
			eval_results = DelayedExpressionEvaluator(
				its_delay_exp,
				fixtures).eval()
			params_with_undelayed_expr[param] = eval_results
		case.setUndelayedExprs(params_with_undelayed_expr)
