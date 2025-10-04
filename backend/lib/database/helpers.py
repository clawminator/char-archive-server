from psycopg2.extras import RealDictCursor

from .connection import CursorFromConnectionFromPool
from ..flask import cache


def get_db_defs():
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        return list({x[0] for x in cursor.fetchall() if x[0].endswith('_def')})


@cache.memoize(timeout=86400)  # 24 hr
def get_hidden_rows(meta_table_name: str, primary_key: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"SELECT {primary_key}, hidden FROM {meta_table_name} WHERE hidden = true")
        rows = cursor.fetchall()
    return rows


def check_node_hidden(meta_table_name: str, primary_key: str, primary_key_value: str):
    hidden_rows = get_hidden_rows(meta_table_name, primary_key)
    for row in hidden_rows:
        if row[primary_key] == primary_key_value:
            return row['hidden']
    return None
