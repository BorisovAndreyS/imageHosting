import datetime
import psycopg
from loguru import logger


class DBManager:
    # Инициализация объекта DBManager
    def __init__(self, dbname: str, user: str, password: str, host: str, port: int):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    # Метод Connect вызывается и возвращает объект psycopg.Connection, но кто его должен вызвать?
    def connect(self) -> psycopg.Connection:
        self.conn = psycopg.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        return self.conn

    # def close(self):
    #     self.conn.close()

    def init_tables(self):
        self.execute_file('db/queries/init_data.sql')

    #
    def execute_file(self, filename: str):
        logger.info('Создаем таблицу images если ее нет')
        try:
            self.execute(open(filename).read())

        except FileNotFoundError:
            logger.error(f'File {filename} not found')

    def execute(self, query: str):
        # if self.conn is None:
        #     logger.error('No connection DB')
        self.conn = self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query)
        self.conn.commit()
    # #
    def get_images(self):
        self.conn = self.connect()
        with self.conn.cursor() as cursor:
            # Выполняем запрос к таблице images
            cursor.execute("SELECT * FROM images")

            # Получаем имена столбцов
            column_names = [desc[0] for desc in cursor.description]

            # Получаем данные
            rows = cursor.fetchall()

            # Преобразуем данные в список словарей
            result = []

            for row in rows:
                row_dict = dict(zip(column_names, row))

                for key, val in row_dict.items():
                    # logger.info(type(val))
                    if type(val) == datetime.datetime:
                        row_dict[key] = val.isoformat()
                result.append(row_dict)
            return result
            # return cursor.fetchall()
    # #
    def add_image(self, filename, orig_name, file_size_kb, ext):
        logger.info(f'Try to add image {filename}')
        self.conn = self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO images "
                "(filename, original_name, size, file_type)"
                "VALUES (%s, %s, %s, %s)",
                (filename, orig_name, file_size_kb, ext)
            )
        self.conn.commit()

