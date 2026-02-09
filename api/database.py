import os
import psycopg

connection = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="silentkey_identity",
    user="sk_app_user",
    password=os.environ.get("SK_DB_PASSWORD", "")
)

print(connection)