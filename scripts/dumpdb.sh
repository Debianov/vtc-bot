#!/bin/bash

if [[ $(dirname $0) == "." ]]; then
	printf "%s\n" "Call script from root repo." >&2 && exit 1
fi

if [[ $# -ne 2 ]]; then
	printf "%s\n" "Usage: $0 <db_name> <db_user>" >&2 && exit 2
fi

echo "Dumping database..."
pg_dump -v -U $2 -d $1 -sxO > schematmp.sql || ( rm schematmp.sql && exit 3 )
echo "Replacing original schema..."
mv schematmp.sql schema.sql
echo "Dumping completed."
