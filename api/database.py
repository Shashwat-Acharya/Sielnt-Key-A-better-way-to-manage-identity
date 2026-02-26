import environ
import psycopg

env = environ.Env()
env.read_env()

connection = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="silentkey_identity",
    user="sk_app_user",
    password=env.str("SK_DB_PASSWORD", "")
)

print(connection)