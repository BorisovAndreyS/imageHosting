import re
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from loguru import logger
from pathlib import Path
import socket

logger.add('logs/app.log', format="[{time:YYYY-MM-DD HH:mm:ss}] | {level} | {message}")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 10 MB
IMAGE_EXTENSION = ['.jpg', '.jpeg', '.png', '.gif']


# SERVER_ADDR = ('0.0.0.0', 8000)


# Функция генерации HTML после успешной загрузки картинки
def generate_upload_success_page(image_id, ext):
    html = ('<!DOCTYPE html>\n'
            '<html>\n'
            '<head>\n'
            '<meta charset="UTF-8">\n'
            '<title>Успешная загрузка</title>\n'
            '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"\n'
            'integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">\n'
            '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"\n'
            'integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"\n'
            'crossorigin="anonymous"></script>'
            '</head>\n'
            '<body class="d-flex min-vh-100 justify-content-center align-items-center bg-light">\n')
    html += '<div class="content-box justify-content-center bg-white col-12 col-md-8 col-lg-6 p-4 rounded-3 shadow">'
    # Заголовок
    html += '<h1 class="mb-4 text-center">Файл успешно загружен</h1>\n'

    # Миниатюра изображения
    html += '<div class="text-center mb-4">\n'
    html += (f'<img src="/images/{image_id}.{ext}" alt="Загруженное изображение" '
             f'class="img-fluid mb-4" style="max-width: 300px; height: auto;">\n')
    html += '</div>\n'

    # Группа кнопок
    html += '<div class="d-flex justify-content-center mb-3">\n'
    html += f'<a href="/images/{image_id}.{ext}" download class="btn btn-primary me-2">Скачать</a>\n'
    html += f'<a href="/upload" class="btn btn-outline-secondary me-2">Загрузить еще</a>\n'
    html += '<a href="/images" class="btn btn-outline-secondary me-2">Каталог</a>\n'
    html += '</div>\n'

    # Ссылка для вставки (пустое поле, которое будет заполнено JavaScript)
    html += '<div class="mb-3">\n'
    html += '<label for="image-url" class="form-label">Ссылка для вставки:</label>\n'
    html += '<input type="text" id="image-url" class="form-control" value = "121223" readonly>\n'
    html += '<button class="btn btn-sm btn-success mt-2 w-100" onclick="copyUrl()">Скопировать ссылку</button>\n'
    html += '</div>\n'

    # Добавляем JavaScript для формирования ссылки и копирования
    html += '<script>\n'
    html += 'document.addEventListener("DOMContentLoaded", function() {\n'
    html += '  const imageUrlInput = document.getElementById("image-url");\n'
    html += '  const imageId = window.location.pathname.split("/").pop(); // Получаем ID изображения\n'
    html += '  const extension = imageId.split(".").pop(); // Получаем расширение\n'
    html += '  const host = window.location.origin; // Текущий домен или IP\n'
    html += '  const fullImageUrl = `${host}/images/${imageId}`;\n'
    html += '  imageUrlInput.value = host; // Заполняем поле ссылкой\n'
    html += '});\n'

    html += 'function copyUrl() {\n'
    html += '  const input = document.getElementById("image-url");\n'
    html += '  input.select();\n'
    html += '  input.setSelectionRange(0, 99999); // Для мобильных устройств\n'
    html += '  navigator.clipboard.writeText(input.value).then(() => {\n'
    html += '      alert("Ссылка скопирована!");\n'
    html += '  }).catch(err => {\n'
    html += '      console.error("Не удалось скопировать ссылку: ", err);\n'
    html += '  });\n'
    html += '}\n'

    html += '</script>\n'

    html += '</div>'

    html += '</body>\n</html>'
    return html


# Функция для генерации HTML страницы каталога
def generate_gallery_page(image_files):
    html = '''<!DOCTYPE html>
    <html lang="ru">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Image Gallery</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .image-item {
            transition: transform 0.2s; /* Добавляем плавную анимацию при наведении */
        }

        .image-item:hover {
            transform: scale(1.05); /* Увеличиваем масштаб элемента при наведении */
        }
    </style>
    </head>
    <body class="bg-light">
    <div class="container py-5">
        <h1 class="text-center mb-4">Загруженные изображения</h1>
        <div class="text-center mb-3">
            <a href="/" class="btn btn-primary">Главная</a>
        </div>
        <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 g-3">
    '''

    for filename in image_files:
        html += f'''
            <div class="col">
                <div class="card shadow-sm image-item">
                    <a href="/images/{filename}" target="_blank">
                        <img src="/images/{filename}" alt="{filename}" class="bd-placeholder-img card-img-top" style="object-fit: cover;
                        height: 200px;">
                    </a>
                    <div class="card-body">
                        <p class="card-text text-center">{filename}</p>
                        <div class="d-flex justify-content-center align-items-center">
                            <a href="/images/{filename}" download class="btn btn-sm btn-outline-secondary">Скачать</a>
                        </div>
                    </div>
                </div>
            </div>
        '''

    html += '''
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    return html
# def generate_gallery_page(image_files):
#     html = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>Image Gallery</title>\n</head>\n<body>\n'
#     html += '<h1>Uploaded Images</h1>\n'
#     html += '<a href="/" style="text-decoration: none;">\n'
#     html += '  <button><p>Главная</p></button>\n'
#     html += '</a>\n'
#
#
#     html += '<div style="display: flex; flex-wrap: wrap;">\n'
#
#     for filename in image_files:
#         html += f'<div style="margin: 10px; text-align: center;">\n'
#         html += f'  <a href="/images/{filename}" target="_blank">\n'  # Используем относительный путь
#         html += f'    <img src="/images/{filename}" alt="{filename}" style="max-width: 200px; max-height: 200px;">\n'
#         html += f'  </a>\n'
#         html += f'  <p>{filename}</p>\n'
#         html += f'<p><a href="/images/{filename}" download>Скачать</a></p>\n'
#         html += '</div>\n'
#
#     html += '</div>\n</body>\n</html>'
#
#     return html


# Функция для формирования списка файлов
def get_image_files(directory):
    image_extensions = ''
    image_files = []

    for file_path in Path(directory).iterdir():
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSION:
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
        self.send_header('Content-Type', 'text/html; charset=utf-8')
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

        extension = filename.split('.')[-1]

        if f".{extension}" not in IMAGE_EXTENSION:
            logger.error(f"Ошибка: неподдерживаемый формат файла .{extension}.")
            self.send_response(400)  # Bad Request
            self.end_headers()
            return

        image_id = uuid.uuid4()

        with open(f'images/{image_id}.{extension}', 'wb') as f:
            f.write(file_content)

        logger.info(f'Успех: Изображение {image_id}.{extension} загружено')
        # Генерируем HTML-страницу с миниатюрой и ссылками
        html_content = generate_upload_success_page(image_id, extension)

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
