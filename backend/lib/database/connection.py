from psycopg2 import pool


class Database:
    __connection_pool = None

    @classmethod
    def initialise(cls, minconn, maxconn, **kwargs):
        if cls.__connection_pool is not None:
            raise Exception('Database connection pool is already initialised')
        cls.__connection_pool = pool.ThreadedConnectionPool(minconn, maxconn, **kwargs)

    @classmethod
    def get_connection(cls):
        return cls.__connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        cls.__connection_pool.putconn(connection)


class CursorFromConnectionFromPool:
    def __init__(self, cursor_factory=None):
        self.conn = None
        self.cursor = None
        self.cursor_factory = cursor_factory

    def __enter__(self):
        self.conn = Database.get_connection()
        self.cursor = self.conn.cursor(cursor_factory=self.cursor_factory)
        return self.cursor

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_value is not None:  # This is equivalent of saying if there is an exception
            self.conn.rollback()
        else:
            self.cursor.close()
            self.conn.commit()
        Database.return_connection(self.conn)
