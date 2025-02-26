FROM python:3.12-alpine
LABEL authors="Helmut"

WORKDIR /app
COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]