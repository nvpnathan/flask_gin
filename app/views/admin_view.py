import os
from dotenv import load_dotenv
from flask_admin.contrib.sqla import ModelView
import psycopg2

load_dotenv()


def get_db_conn():
    conn = psycopg2.connect(
            host=os.environ['POSTGRES_SERVER'],
            database=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'])
    return conn


class WinnerView(ModelView):
    def get_session(self):
        return get_db_conn()

    column_searchable_list = ('name',)
    column_filters = ('score', 'hands_won', 'num_gins', 'num_undercuts')

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):

        conn = get_db_conn()
        cursor = conn.cursor()
        query = "SELECT name, score, hands_won, num_gins, num_undercuts FROM winner"
        if search:
            query += f" WHERE name ILIKE '%{search}%'"
        if filters:
            query += f" WHERE {' AND '.join([f'{f[0]} = {f[1]}' for f in filters])}"
        if sort_field:
            query += f" ORDER BY {sort_field} {'DESC' if sort_desc else 'ASC'}"
        if page_size:
            query += f" LIMIT {page_size} OFFSET {(page - 1) * page_size}"
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results, len(results)
