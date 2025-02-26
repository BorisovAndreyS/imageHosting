import re
import sys
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from loguru import logger

logger.add('logs/app.log', format="[{time:YYYY-MM-DD HH:mm:ss}] | {level} | {message}")

# import logger
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
SERVER_ADDR = ('localhost', 8000)

#Функция для генерации HTML страницы каталога
def generate_gallery_page(image_files, base_url):
    html = '<!DOCTYPE html>\n<html>\n<head>\n<title>Image Gallery</title>\n</head>\n<body>\n'
    html += '<h1>Uploaded Images</h1>\n'
    html += '<div style="display: flex; flex-wrap: wrap;">\n'

    for filename in image_files:
        html += f'<div style="margin: 10px; text-align: center;">\n'
        html += f'  <a href="{base_url}/{filename}" target="_blank">\n'
        html += f'    <img src="{base_url}/{filename}" alt="{filename}" style="max-width: 200px; max-height: 200px;">\n'
        html += f'  </a>\n'
        html += f'  <p>{filename}</p>\n'
        html += '</div>\n'

    html += '</div>\n</body>\n</html>'
    return html
#Функция для формирования списка файлов
def get_image_files(directory):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    image_files = []

    for file_path in Path(directory).iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path.name)

    return image_files

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

    def do_GET(self):
        if self.path == '/images':
            directory = 'images'
            base_url = f'http://{SERVER_ADDR[0]}:{SERVER_ADDR[1]}/images'
            image_files = get_image_files(directory)

            html_content = generate_gallery_page(image_files, base_url)

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            return

        if self.path == '/upload':
            directory = 'upload'
            base_url = f'http://{SERVER_ADDR[0]}:{SERVER_ADDR[1]}/upload'
            image_files = get_image_files(directory)

            html_content = generate_gallery_page(image_files, base_url)

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            return
        # if self.path in ('/', '/index.html'):
        #     logger.info(f'GET {self.path}')
        #     self.send_response(200)
        #     self.send_header('Content-type', 'text/html; charset=utf-8')
        #     self.end_headers()
        #     self.wfile.write(open('index.html', 'rb').read())
        # else:
        #     logger.warning(f'GET {self.path}')
        #     self.send_response(400)

    def do_POST(self):
        if self.path == '/upload':
            logger.info(f'POST {self.path}')
            content_length = int(self.headers.get('Content-Length', 0))

            if content_length == 0:
                logger.warning("Missing Content-Length header")
                self.send_response(411)  # Length Required
                self.end_headers()
                return

            #Проверяем Content-Type, через форму должен прйти multipart/form-data
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

            image_id = uuid.uuid4()


            with open(f'app/images/{image_id}.jpg', 'wb') as f:
                f.write(file_content)

            logger.info(f'Upload succes {self.path}')
            self.send_response(201)
            self.send_header('Location', f'http://{SERVER_ADDR[0]}:{SERVER_ADDR[1]}/images/{image_id}.jpg')
            self.end_headers()

        else:
            self.send_response(405, 'Method not Allowed')









def run():
    server_address = ('localhost', 8000)
    httpd = HTTPServer(server_address, ImageHostingHandler)
    try:
        print(f'Serving at http://{server_address[0]}:{server_address[1]}')
        httpd.serve_forever()
    except Exception:
        pass
    finally:
        httpd.server_close()




if __name__ == '__main__':
    run()