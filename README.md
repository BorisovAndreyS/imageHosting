**Проект ImageHosting**

Сервис работает на Docker. 
Использует два микросервиса:
- nginx - Frontend
- python 3.12 - Backend

Хранение картинок и логов реализвано с использованием томов


**1. Как развернуть сервис**

- Установить Docker, пример для Ubuntu 
  - `apt update`
  - `apt install sudo`
  - `sudo apt-get install ca-certificates curl`
  - `sudo install -m 0755 -d /etc/apt/keyrings`
  - `sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc`
  - `sudo chmod a+r /etc/apt/keyrings/docker.asc`
  - `echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null`
  - `sudo apt-get update`
  - `sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin`
- Проверим версию:
  - `docker compose version`
- Скачать файлы проекта
  - `git clone https://github.com/BorisovAndreyS/imageHosting`
  - `cd imageHosting`
- Развернуть проект в среде Docker
  - `docker compose up --build`

**2. Как пользоваться**

- Главная страница (`http://Ваш ip адрес/`)
- Страница загрузки изображений (`http://Ваш ip адрес/upload`).
- Каталог загруженных изображений (`http://Ваш ip адрес/images/`).
- Загружать фотки в популярных форматах (.jpg, .png, .gif).

