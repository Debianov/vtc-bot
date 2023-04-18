#!/bin/sh

if [ ! -f schema.sql ]; then
	echo "Can't find schema.sql. You running script from root repo?" >&2
	exit 1
fi

if [ $# -ne 2 ]; then
	echo "Usage: $0 <db_name> <db_user>" >&2
	exit 2
fi

echo "Creating tables..."
psql --set=ON_ERROR_STOP=1 --username="$2" --dbname="$1" --file=schema.sql --echo-errors 2>&1 >/dev/null || exit 3
echo "Tables created."
