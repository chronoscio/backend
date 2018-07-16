#!/bin/bash
# wait-for-postgres.sh

set -e

dbname="postgres"
host="db"
port="5432"
user="postgres"
passwd="postgres"
cmd="$@"

>&2 echo "Waiting for Postgres..."

python wait_for_postgres.py $dbname $host $port $user $passwd

>&2 echo "Postgres is up - executing command"

python manage.py makemigrations
python manage.py migrate

exec $cmd
#gunicorn interactivemap.wsgi -b 0.0.0.0:80