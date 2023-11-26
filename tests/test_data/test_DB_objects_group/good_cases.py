from typing import Dict, Tuple, Union, Any, List
import pytest

from utils import DelayedExpression
from bot.mock import IDHolder

from psycopg import AsyncConnection
from bot.data import TargetGroupAttrs


class CaseForTargetGroup(TargetGroupAttrs):
	pass


class GoodCasesForTargetGroup:

	def getCaseWithoutNone(self) \
			-> Tuple[CaseForTargetGroup, CaseForTargetGroup]:
		without_none = {
			"dbconn": DelayedExpression("db"),
			"context_id": 1,
			"target": IDHolder(1),
			"act": IDHolder(1),
			"d_in": [IDHolder(3), IDHolder(2)],
			"name": "sudo",
			"output": "deb",
			"priority": 2,
			"other": 2,
			"dbrecord_id": 3
		}

		expect_result = {
			"dbconn": DelayedExpression("db"),
			"context_id": 1,
			"target": IDHolder(1),
			"act": IDHolder(1),
			"d_in": [IDHolder(3), IDHolder(2)],
			"name": "sudo",
			"output": "deb",
			"priority": 2,
			"other": 2,
			"dbrecord_id": 3
		}

		return (CaseForTargetGroup(**without_none),
				CaseForTargetGroup(**expect_result))

	def getCaseWithNone(self) -> Tuple[CaseForTargetGroup, CaseForTargetGroup]:
		with_none = {
			"dbconn": DelayedExpression("db"),
			"context_id": 1,
			"target": IDHolder(1),
			"act": IDHolder(1),
			"d_in": [IDHolder(3), IDHolder(2)],
			"name": None,
			"output": None,
			"priority": None,
			"other": None,
			"dbrecord_id": 0
		}

		expect_result = {
			"dbconn": DelayedExpression("db"),
			"context_id": 1,
			"target": IDHolder(1),
			"act": IDHolder(1),
			"d_in": [IDHolder(3), IDHolder(2)],
			"name": None,
			"output": None,
			"priority": None,
			"other": None,
			"dbrecord_id": 0
		}

		return (CaseForTargetGroup(**with_none),
				CaseForTargetGroup(**expect_result))

	def getCaseWithNoneExceptDBRecordID(self) \
			-> Tuple[CaseForTargetGroup, CaseForTargetGroup]:
		with_none_except_id = {
			"dbconn": DelayedExpression("db"),
			"context_id": 1,
			"target": IDHolder(1),
			"act": IDHolder(1),
			"d_in": [IDHolder(3), IDHolder(2)],
			"name": None,
			"output": None,
			"priority": None,
			"other": None,
			"dbrecord_id": 1
		}

		expect_result = {
			"dbconn": DelayedExpression("db"),
			"context_id": 0,
			"target": IDHolder(1),
			"act": IDHolder(1),
			"d_in": [IDHolder(3), IDHolder(2)],
			"name": None,
			"output": None,
			"priority": None,
			"other": None,
			"dbrecord_id": 1
		}

		return (
			CaseForTargetGroup(**with_none_except_id),
			CaseForTargetGroup(**expect_result)
		)