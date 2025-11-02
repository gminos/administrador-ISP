#!/bin/bash

set -e

echo "tranqui... se esta esperando la base datos"
while ! nc -z db 5432; do
  sleep 1
done

echo "se empieza a aplicar migraciones"
uv run python manage.py migrate --verbosity 0

echo "generando los archivo estaticos... calmado"
uv run python manage.py collectstatic --noinput --verbosity 0

echo "se va a iniciar el servidor Django"
exec "$@"
