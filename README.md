**Проект ImageHosting**

Сервис работает на Docker. 
Использует два микросервиса:
- nginx - Frontend
- python 3.12 - Backend

Хранение картинок и логов реализвано с использованием томов


**1. Как развернуть сервис**

- Установить Docker, пример для Ubuntu 
  - `sudo curl -L "https://github.com/docker/compose/releases/download/2.2.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`
  - `sudo chmod +x /usr/local/bin/docker-compose`
- Проверим версию:
  - `docker-compose --version`
- Скачать файлы проекта
  - `git clone https://github.com/BorisovAndreyS/imageHosting`
  - `cd imageHosting`
- Развернуть проект в среде Docker
  - `docker-compose up --build`

**2. Как пользоваться**

- Главная страница (`http://Ваш ip адрес/`)
- Страница загрузки изображений (`http://Ваш ip адрес/upload`).
- Каталог загруженных изображений (`http://Ваш ip адрес/images/`).
- Загружать фотки в популярных форматах (.jpg, .png, .gif).

