import psycopg2

def connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="eWalletDatabase",
            user="admin",
            password="admin")
        print('Connect to database successfully')
    except Exception as e:
        print('Can\'t connect to database, error:' + str(e))
    return conn
