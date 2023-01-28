import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="gin_db",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute('CREATE TABLE IF NOT EXISTS player (player_id SERIAL PRIMARY KEY,'
            'name VARCHAR(255) NOT NULL,'
            'score INTEGER NOT NULL,'
            'hands_won INTEGER NOT NULL,'
            'num_gins INTEGER NOT NULL,'
            'date_added date DEFAULT CURRENT_TIMESTAMP);')

cur.execute('CREATE TABLE IF NOT EXISTS player (winner_id SERIAL PRIMARY KEY,'
            'name VARCHAR(255) NOT NULL,'
            'score INTEGER NOT NULL,'
            'hands_won INTEGER NOT NULL,'
            'num_gins INTEGER NOT NULL,'
            'date_added date DEFAULT CURRENT_TIMESTAMP);')

conn.commit()

cur.close()
conn.close()
