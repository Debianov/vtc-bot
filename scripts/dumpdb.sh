#!/bin/sh

if [ ! -f schema.sql ]; then
	echo "Can't find schema.sql. You running script from root repo?" >&2
	exit 1
fi

if [ $# -ne 2 ]; then
	echo "Usage: $0 <db_name> <db_user>" >&2
	exit 2
fi

echo "Dumping database..."
pg_dump --username="$2" --dbname="$1" --schema-only --no-privileges --no-owner --clean --if-exists > schematmp.sql || { rm schematmp.sql; exit 3; }
echo "Replacing original schema..."
mv schematmp.sql schema.sql
echo "Dumping completed."
