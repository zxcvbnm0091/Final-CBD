import psycopg2

def db_connection():
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='cbd',
        user='postgres',
        password='admin'
    )
    return conn