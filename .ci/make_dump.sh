#!/usr/bin/env bash

# exit immediately if a any command exits with a non-zero status
set -e

if [ -z ${CYBERBOX_TEST_DB_URL} ]; then
    echo "ERROR: CYBERBOX_TEST_DB_URL variable is empty. Export like this:" >&2
    exit 1
fi

# full directory name of the script no matter where it is being called from
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
DIR="${DIR%/}"

METHOD="$1"
URL="$CYBERBOX_TEST_DB_URL"

python3 "${DIR}/upgrade_db.py" --method "$METHOD" >&2
pg_dump "$URL" -s --no-owner | sed '/^--/d' | python "${DIR}/sort_dump.py"
