from typing import Any

import psycopg
import pytest

from bot.attrs import TargetGroupAttrs
from bot.data import TargetGroup
from bot.utils import Case

from .good_cases import (
	case_with_none,
	case_with_none_except_db_record_id,
	case_without_none,
	expect_case_for_case_with_none
)


@pytest.mark.doDelayedExpression
@pytest.mark.parametrize(
	"pass_args, expect_args",
	[
		(case_without_none, case_without_none),
		(case_with_none, expect_case_for_case_with_none),
		(case_with_none_except_db_record_id, case_with_none_except_db_record_id)
	]
)
def test_init_target_group(
	db: psycopg.AsyncConnection[Any],
	pass_args: Case,
	expect_args: Case
):
	instance = TargetGroup(TargetGroupAttrs(**pass_args))  # type: ignore [arg-type]
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