#Check if postgres is running or not
import psycopg2
import time

while True:
    try:
        conn = psycopg2.connect("dbname='postgres' user='postgres' host='db'")
        print('connected')
        break
    except Exception as ex:
        print(ex)
        time.sleep(0.5)
