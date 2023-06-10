#!/bin/sh

set -e

host="$1"
shift

until PGPASSWORD="$DB_PASSWORD" psql -h "$host" -d "$DB_NAME" -U "$DB_USER" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec "$@"
