import os
import re
import urllib
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from loguru import logger
from pathlib import Path
from db.DBManager import DBManager
import json

logger.add('logs/app.log', format="[{time:YYYY-MM-DD HH:mm:ss}] | {level} | {message}")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 10 MB
IMAGE_EXTENSION = ['.jpg', '.jpeg', '.png', '.gif']


# Функция генерации HTML после успешной загрузки картинки - Это переделать!!!!
def generate_upload_success_page(image_id, ext):
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Успешная загрузка</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"
          integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"
            crossorigin="anonymous"></script>
</head>
<body class="d-flex min-vh-100 justify-content-center align-items-center bg-light">
<div class="content-box justify-content-center bg-white col-12 col-md-8 col-lg-6 p-4 rounded-3 shadow">
    <h1 class="mb-4 text-center">Файл успешно загружен</h1>

    <!-- Миниатюра изображения -->
    <div class="text-center mb-4">
        <img src="/images/{image_id}.{ext}" alt="Загруженное изображение" 
             class="img-fluid mb-4" style="max-width: 300px; height: auto;">
    </div>

    <!-- Группа кнопок -->
    <div class="d-flex justify-content-center mb-3">
        <a href="/images/{image_id}.{ext}" download class="btn btn-primary me-2">Скачать</a>
        <a href="/upload" class="btn btn-outline-secondary me-2">Загрузить еще</a>
        <a href="/all_images" class="btn btn-outline-secondary me-2">Каталог</a>
        <a href="/images-list" class="btn btn-outline-secondary me-2">Таблица
            изображений</a>
    </div>

    <!-- Ссылка для вставки -->
    <div class="mb-3">
        <label for="image-url" class="form-label">Ссылка для вставки:</label>
        <input type="text" id="image-url" class="form-control" value="/images/{image_id}.{ext}" readonly>
        <button class="btn btn-sm btn-success mt-2 w-100" onclick="copyUrl()">Скопировать ссылку</button>
    </div>

    <!-- JavaScript для формирования полной ссылки и копирования -->
    <script>
        document.addEventListener("DOMContentLoaded", function () {{
            const host = window.location.origin;
            const relativePath = document.getElementById("image-url").value;
            const fullPath = `${{host}}${{relativePath}}`;
            document.getElementById("image-url").value = fullPath;
        }});

        function copyUrl() {{
            const input = document.getElementById("image-url");
            input.select();
            input.setSelectionRange(0, 99999); // Для мобильных устройств
            navigator.clipboard.writeText(input.value).then(() => {{
                alert("Ссылка скопирована!");
            }}).catch(err => {{
                console.error("Не удалось скопировать ссылку: ", err);
            }});
        }}
    </script>
</div>
</body>
</html>
'''

    return html


# Парсер для распаковки multipart/form-data данных отправленных с формы
# парсер нужен 100%
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
    db = DBManager(os.getenv('POSTGRES_DB'),
                   os.getenv('POSTGRES_USER'),
                   os.getenv('POSTGRES_PASSWORD'),
                   os.getenv('POSTGRES_HOST'),
                   os.getenv('POSTGRES_PORT')
                   )

    def setup(self):
        super().setup()
        self.get_routes = {
            '/upload': self.get_upload,
            '/api/all_images/': self.get_images_list,
            '/api/images-list/': self.get_images_list,
        }

        self.post_routes = {
            '/upload': self.post_upload,
        }

        self.delete_routes = {
            '/api/delete/': self.delete_images,
        }

    def do_DELETE(self):
        logger.info(f'self path {self.path}')
        # Проверяем, соответствует ли путь одному из ключей в delete_routes
        for route, handler in self.delete_routes.items():
            if self.path.startswith(route):
                # logger.info('УРАА МЫ ТУТ!!!')
                handler()
                return

    def delete_images(self):
        logger.info(f'Попали в delete_images для пути: {self.path}')

        path_parts = self.path.split('/')
        image_id = path_parts[3]

        self.db.delete_image(image_id)

    def do_GET(self):
        if self.path in self.get_routes:
            self.get_routes[self.path]()
        else:
            logger.warning(f'GET 404 {self.path}')
            self.send_response(404, 'Not found')

    def do_POST(self):
        if self.path in self.post_routes:
            self.post_routes[self.path]()
        else:
            self.send_response(404)
            logger.warning(f'POST 404 {self.path}')
            self.end_headers()
            self.wfile.write(b'Not Found')

    def get_images_list(self):
        try:
            # logger.info(f'Пришел запрос {self.path}')
            list_images = self.db.get_images()
            # logger.info(f'List images: {list_images}')
            json_data = json.dumps(list_images, ensure_ascii=False, indent=4)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()

            self.wfile.write(json_data.encode('utf-8'))
        except Exception as e:
            logger.error(f'get_images_list Error {e}')
            # Возвращаем JSON-ошибку клиенту
            error_data = {"error": "Internal server error"}
            json_error = json.dumps(error_data).encode('utf-8')

            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json_error)

    def get_upload(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(open('static/upload.html', 'rb').read())
        return

    def post_upload(self):
        content_length = int(self.headers.get('Content-Length', 0))

        if content_length == 0:
            logger.warning("Missing Content-Length header")
            self.send_response(411)  # Length Required
            self.end_headers()
            return

        # Проверяем Content-Type, через форму должен прийти multipart/form-data
        content_type = self.headers.get('Content-Type', '')

        if 'multipart/form-data' in content_type:
            try:
                orig_name, file_content = parse_multipart_form_data(self.headers, self.rfile, content_length)
            except ValueError as e:
                logger.error(f"Error parsing multipart/form-data: {e}")
                self.send_response(400)  # Bad Request
                self.end_headers()
                return
        else:
            # Прямое чтение бинарных данных
            file_content = self.rfile.read(content_length)
            orig_name = None

        extension = orig_name.split('.')[-1]

        if f".{extension}" not in IMAGE_EXTENSION:
            logger.error(f"Ошибка: неподдерживаемый формат файла .{extension}.")
            self.send_response(400)  # Bad Request
            self.end_headers()
            return

        filename = uuid.uuid4()

        file_size_kb = round(content_length / 1024)

        # #Запишем данные в таблицу

        self.db.add_image(filename, orig_name, file_size_kb, extension)

        with open(f'images/{filename}.{extension}', 'wb') as f:
            f.write(file_content)

        logger.info(f'Успех: Изображение {filename}.{extension} загружено')
        # Генерируем HTML-страницу с миниатюрой и ссылками
        html_content = generate_upload_success_page(filename, extension)

        # Отправляем HTML-страницу в ответ
        self.send_response(200)  # OK
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(html_content.encode('utf-8')))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))


def run():
    db = DBManager(os.getenv('POSTGRES_DB'),
                   os.getenv('POSTGRES_USER'),
                   os.getenv('POSTGRES_PASSWORD'),
                   os.getenv('POSTGRES_HOST'),
                   os.getenv('POSTGRES_PORT'))
    # db.connect()
    db.init_tables()
    # logger.info(db.get_images())
    # logger.info(db.get_images())
    # db.close()
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
