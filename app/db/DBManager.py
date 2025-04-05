import psycopg
from loguru import logger

class DBManager:
    try:
        def __init__(self, dbname: str, user: str, password: str, host: str, port: int):
            self.dbname = dbname
            self.user = user
            self.password = password
            self.host = host
            self.port = port
            self.conn = None
    except psycopg.Error as e:
        logger.error(f'DB connection: {e}')

    def connect(self) -> psycopg.Connection:
        self.conn = psycopg.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        return self.conn



    def close(self):
        self.conn.close()


    def init_tables(self):
        self.execute_file('db/queries/init_data.sql')

    def execute_file(self, filename: str):
        try:
            self.execute(open(filename).read())
        except FileNotFoundError:
            logger.error(f'File {filename} not found')

    def execute(self, query: str):
        with self.connect().cursor() as cursor:
            cursor.execute(query)

    def get_images(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM images")
            return cursor.fetchall()

