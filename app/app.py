import re
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from loguru import logger
from pathlib import Path
import socket

logger.add('logs/app.log', format="[{time:YYYY-MM-DD HH:mm:ss}] | {level} | {message}")

# import logger - РАБОТАЕТ!!!!!
MAX_FILE_SIZE = 5 * 1024 * 1024  # 10 MB

SERVER_ADDR = ('0.0.0.0', 8000)


# Функция генерации HTML после успешной загрузки картинки
def generate_upload_success_page(image_id):
    html = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>Успешная загрузка</title>\n</head>\n<body>\n'
    html += '<h1>Файл успешно загружен</h1>\n'

    # Миниатюра изображения
    html += f'<img src="/images/{image_id}.jpg" alt="Загруженная картинка" style="max-width: 300px; max-height: 300px;">\n'

    # Ссылка на скачивание
    html += f'<p><a href="/images/{image_id}.jpg" download>Скачать</a></p>\n'

    # Ссылка на галерею
    html += '<p><a href="/images">Каталог</a></p>\n'

    html += '</body>\n</html>'
    return html


# Функция для генерации HTML страницы каталога
def generate_gallery_page(image_files):
    html = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>Image Gallery</title>\n</head>\n<body>\n'
    html += '<h1>Uploaded Images</h1>\n'
    html += '<a href="/" style="text-decoration: none;">\n'
    html += '  <button><p>Главная</p></button>\n'
    html += '</a>\n'

    html += '<div style="display: flex; flex-wrap: wrap;">\n'

    for filename in image_files:
        html += f'<div style="margin: 10px; text-align: center;">\n'
        html += f'  <a href="/images/{filename}" target="_blank">\n'  # Используем относительный путь
        html += f'    <img src="/images/{filename}" alt="{filename}" style="max-width: 200px; max-height: 200px;">\n'
        html += f'  </a>\n'
        html += f'  <p>{filename}</p>\n'
        html += f'<p><a href="/images/{filename}.jpg" download>Скачать</a></p>\n'
        html += '</div>\n'

    html += '</div>\n</body>\n</html>'
    return html


# Функция для формирования списка файлов
def get_image_files(directory):
    image_extensions = ImageHostingHandler.image_extensions
    image_files = []

    for file_path in Path(directory).iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path.name)

    return image_files, image_extensions


# Парсер для распаковки multipart/form-data данных отправленных с формы
def parse_multipart_form_data(headers, rfile, content_length):
    content_type = headers.get('Content-Type', '')
    if 'multipart/form-data' not in content_type:
        raise ValueError("Not a multipart/form-data request")

    boundary = content_type.split('boundary=')[1]
    if not boundary:
        raise ValueError("Boundary not found in Content-Type header")

    boundary = bytes(f"--{boundary}", 'utf-8')
    raw_data = rfile.read(content_length)

    # Разделяем данные по границе
    parts = raw_data.split(boundary)
    for part in parts:
        if not part.strip():  # Пропускаем пустые части
            continue

        # Ищем имя файла и MIME-тип
        match = re.search(rb'filename="([^"]+)"', part)
        if match:
            filename = match.group(1).decode('utf-8')

            # Ищем начало бинарных данных
            match = re.search(rb'\r\n\r\n(.+)', part, re.DOTALL)
            if match:
                file_content = match.group(1)
                return filename, file_content

    raise ValueError("No file part found in multipart request")


class ImageHostingHandler(BaseHTTPRequestHandler):
    server_version = 'ImageHosting'
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']

    routes_GET = {
        '/images': 'get_images',
        '/upload': 'get_upload',
    }

    routes_POST = {
        '/upload': 'post_upload',
    }

    def do_GET(self):
        logger.info(f'GET {self.path}')
        if self.path in self.routes_GET:
            exec(f'self.{self.routes_GET[self.path]}()')
        else:
            logger.warning(f'GET 404 {self.path}')
            self.send_response(404, 'Not found')

    def do_POST(self):
        logger.info(f'POST {self.path}')
        if self.path in self.routes_POST:
            exec(f'self.{self.routes_POST[self.path]}()')
        else:
            self.send_response(404)
            logger.warning(f'POST 404 {self.path}')
            self.end_headers()
            self.wfile.write(b'Not Found')

    def get_images(self):
        directory = 'images'
        image_files, image_extension = get_image_files(directory)

        html_content = generate_gallery_page(image_files)

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
        return

    def get_upload(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(open('upload.html', 'rb').read())
        return

    def post_upload(self):
        logger.info(f'POST {self.path}')
        content_length = int(self.headers.get('Content-Length', 0))

        if content_length == 0:
            logger.warning("Missing Content-Length header")
            self.send_response(411)  # Length Required
            self.end_headers()
            return

        # Проверяем Content-Type, через форму должен прйти multipart/form-data
        content_type = self.headers.get('Content-Type', '')

        if 'multipart/form-data' in content_type:

            try:
                filename, file_content = parse_multipart_form_data(self.headers, self.rfile, content_length)
            except ValueError as e:
                logger.error(f"Error parsing multipart/form-data: {e}")
                self.send_response(400)  # Bad Request
                self.end_headers()
                return
        else:
            # Прямое чтение бинарных данных
            file_content = self.rfile.read(content_length)
            filename = None

        extension = filename.split(sep='.')

        if extension not in ImageHostingHandler.image_extensions:
            logger.error(f"Ошибка: неподдерживаемый формат файла .{extension[-1]}.")
            self.send_response(400)  # Bad Request
            self.end_headers()
            return


        image_id = uuid.uuid4()

        with open(f'images/{image_id}.{extension[-1]}', 'wb') as f:
            f.write(file_content)

        logger.info(f'Успех: Изображение {image_id}.{extension[-1]} загружено')
        # Генерируем HTML-страницу с миниатюрой и ссылками
        html_content = generate_upload_success_page(image_id)

        # Отправляем HTML-страницу в ответ
        self.send_response(200)  # OK
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(html_content.encode('utf-8')))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))


def run():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, ImageHostingHandler)
    try:
        httpd.serve_forever()
    except Exception:
        pass
    finally:
        httpd.server_close()


if __name__ == '__main__':
    run()
