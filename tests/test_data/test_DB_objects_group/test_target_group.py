from typing import Any

import psycopg

from bot.data import TargetGroup
from bot.mock import IDHolder


def test_init_target_group(
	db: psycopg.AsyncConnection[Any],
):
	args = {
		"dbconn": db,
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
	instance = TargetGroup(**args)  # type: ignore [arg-type]
	assert instance.dbconn == args["dbconn"]
	assert instance.context_id == args["context_id"]
	assert instance.target == args["target"]
	assert instance.act == args["act"]
	assert instance.d_in == args["d_in"]
	assert instance.name == args["name"]
	assert instance.output == args["output"]
	assert instance.priority == args["priority"]
	assert instance.other == args["other"]
	assert instance.dbrecord_id == args["dbrecord_id"]