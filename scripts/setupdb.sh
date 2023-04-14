#!/bin/bash

if [[ ! -f schema.sql ]]; then
	printf "%s\n" "Can't find schema.sql. You running script from root repo?" >&2 && exit 1
fi

if [[ $# -ne 2 ]]; then
	printf "%s\n" "Usage: $0 <db_name> <db_user>" >&2 && exit 2
fi

echo "Creating tables..."
psql -v ON_ERROR_STOP=1 -U $2 -d $1 -f schema.sql 2>&1 >/dev/null || exit 3
echo "Tables created."
