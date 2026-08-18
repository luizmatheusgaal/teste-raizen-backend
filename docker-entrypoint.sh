#!/bin/sh
set -e

case "$DB_ENGINE" in
  *postgresql*)
    echo "Waiting for database at ${DB_HOST:-db}:${DB_PORT:-5432}..."
    while ! python -c "import socket; socket.create_connection(('${DB_HOST:-db}', int('${DB_PORT:-5432}')))" >/dev/null 2>&1; do
      sleep 1
    done
    echo "Database is up."
    ;;
esac

echo "Running migrations..."
python manage.py migrate

echo "Starting command: $@"
exec "$@"
