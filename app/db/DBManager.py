import datetime
import os

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

    # Метод Connect вызывается и возвращает объект psycopg.Connection
    def connect(self) -> psycopg.Connection:
        self.conn = psycopg.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        return self.conn

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

        self.conn = self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(query)
        self.conn.commit()

    # Метод делает запрос всех изображений в базе Images и возвращает
    def get_images(self):
        self.conn = self.connect()
        with self.conn.cursor() as cursor:
            # Выполняем запрос к таблице images
            cursor.execute("SELECT * FROM images ORDER BY upload_time DESC")

            # Получаем имена столбцов
            column_names = [desc[0] for desc in cursor.description]

            # Получаем данные
            rows = cursor.fetchall()

            # Преобразуем данные в список словарей
            result = []

            for row in rows:
                row_dict = dict(zip(column_names, row))

                for key, val in row_dict.items():
                    if type(val) == datetime.datetime:
                        row_dict[key] = val.strftime('%Y-%m-%d %H:%M:%S')
                result.append(row_dict)
            return result

    # метод добавляет изображение в базу данных
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

    # метод удаляет изображение из базы данных и диск
    def delete_image(self, id):
        logger.info(f'Началось удаление изображения с id: {id}')

        try:
            self.conn = self.connect()

            # ищем запись в таблице
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT filename, file_type FROM images WHERE id = %s", (id,))

                # Получаем данные
                rows = cursor.fetchone()

                filename, file_type = rows

            self.conn.commit()

            # удаляем файл на диске
            file_path = f"images/{filename}.{file_type}"
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Файл с именем : {file_path} успешно удален")
            else:
                logger.info(f"Файл не найден : {file_path}")

            # удаляем запись в базе данных
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM images WHERE id = %s", (id,))

                self.conn.commit()
                logger.info(f'Запись с ID {id} успешно удалена из базы данных')
        except Exception as e:
            logger.error(f"Ошибка при удалении изображения {str(e)}")
            self.conn.rollback()
            raise

        finally:
            if self.conn:
                self.conn.close()
