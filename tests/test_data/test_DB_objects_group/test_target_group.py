from typing import Any
import pytest
import psycopg

from bot.data import TargetGroup
from bot.mock import IDHolder
from good_cases import GoodCasesForTargetGroup, TargetGroupAttrs

@pytest.mark.doDelayedExpression
@pytest.mark.parametrize(
	"pass_args, expect_args",
	[
		GoodCasesForTargetGroup().getCaseWithoutNone(),
		GoodCasesForTargetGroup().getCaseWithNone(),
		GoodCasesForTargetGroup().getCaseWithNoneExceptDBRecordID()
	]
)
def test_init_target_group(
		db: psycopg.AsyncConnection[Any],
		pass_args: TargetGroupAttrs,
		expect_args: TargetGroupAttrs
):
	instance = TargetGroup(**pass_args)  # type: ignore [arg-type]
	assert instance.dbconn == expect_args["dbconn"]
	assert instance.context_id == expect_args["context_id"]
	assert instance.target == expect_args["target"]
	assert instance.act == expect_args["act"]
	assert instance.d_in == expect_args["d_in"]
	assert instance.name == expect_args["name"]
	assert instance.output == expect_args["output"]
	assert instance.priority == expect_args["priority"]
	assert instance.other == expect_args["other"]
	assert instance.dbrecord_id == expect_args["dbrecord_id"]