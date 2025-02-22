import email
import re
from email.policy import default
from email.policy import HTTP
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler

import logger

SERVER_ADDR = ('localhost', 8000)

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
        if self.path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(open('index.html', 'rb').read())
        else:
            self.send_response(400)

    def do_POST(self):
        if self.path == '/upload':
            content_length = int(self.headers.get('Content-Length', 0))

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


            with open(f'images/{image_id}.jpg', 'wb') as f:
                f.write(file_content)

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