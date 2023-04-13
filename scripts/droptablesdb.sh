#!/bin/bash

if [[ $# -ne 2 ]]; then
	printf "%s\n" "Usage: $0 <db_name> <db_user>" >&2 && exit 1
fi

read -p "Are you sure for DROP ALL TABLES IN DATABASE (y/n)? " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
	exit 2
fi

echo "Droping schema..."
psql -v ON_ERROR_STOP=1 -U $2 -d $1 -c "DROP SCHEMA public CASCADE;" 2>&1 >/dev/null || exit 3
echo "Creating schema..."
psql -v ON_ERROR_STOP=1 -U $2 -d $1 -c "CREATE SCHEMA public;" 2>&1 >/dev/null || exit 4
echo "All tables droped."
