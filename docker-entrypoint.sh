#!/bin/sh
set -eu

if [ ! -s /data/resources/database.db ]; then
    echo "Missing database: restore your backup to data/resources/database.db before starting." >&2
    exit 1
fi

if [ ! -w /data ] || [ ! -w /data/resources ] || [ ! -w /data/resources/database.db ]; then
    echo "Data is not writable. Set LOCAL_UID and LOCAL_GID in .env to the data owner's IDs." >&2
    exit 1
fi

exec "$@"
