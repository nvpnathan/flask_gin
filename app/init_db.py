import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
        host=os.environ['POSTGRES_SERVER'],
        database=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'])

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute('CREATE TABLE IF NOT EXISTS player (player_id SERIAL PRIMARY KEY,'
            'name VARCHAR(255) NOT NULL,'
            'score INTEGER NOT NULL,'
            'hands_won INTEGER NOT NULL,'
            'num_gins INTEGER NOT NULL,'
            'date_added date DEFAULT CURRENT_TIMESTAMP);')

cur.execute('CREATE TABLE IF NOT EXISTS winner (winner_id SERIAL PRIMARY KEY,'
            'name VARCHAR(255) NOT NULL,'
            'score INTEGER DEFAULT 0,'
            'hands_won INTEGER DEFAULT 0,'
            'num_gins INTEGER DEFAULT 0,'
            'num_undercuts INTEGER DEFAULT 0,'
            'date_added date DEFAULT CURRENT_TIMESTAMP);')

conn.commit()

cur.close()
conn.close()
