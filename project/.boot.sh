#!/bin/bash

# wait for Postgres to start
function postgres_ready(){
python << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="postgres")
    conn.close()
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

python manage.py makemigrations 
python manage.py migrate 
gunicorn interactivemap.wsgi -b 0.0.0.0:80