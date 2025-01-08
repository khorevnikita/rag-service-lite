# Используем официальный образ Python как родительский образ
FROM python:3.10-slim

# Установка зависимостей
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc librdkafka-dev netcat-traditional wget poppler-utils build-essential libpq-dev ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Установим рабочую директорию в контейнере
WORKDIR /app

RUN mkdir -p ~/.postgresql && \
wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
     --output-document ~/.postgresql/root.crt && \
chmod 0600 ~/.postgresql/root.crt


# Копируем файлы зависимостей в рабочую директорию
COPY requirements.txt .

# Установка и настройка виртуального окружения
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Устанавливаем любые зависимости, содержащиеся в файле requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем переменные окружения
COPY .env .

# Копируем содержимое локальной директории в рабочую директорию контейнера
COPY . .

# Сообщаем Docker, что контейнер слушает запросы на этом порту во время выполнения
EXPOSE 8000

# Определяем переменные окружения для gunicorn
ENV MODULE_NAME="main"
ENV VARIABLE_NAME="app"
ENV APP_ENV="production"
ENV PYTHONPATH=/app

# Устанавливаем скрипт entrypoint.sh в качестве точки входа
ENTRYPOINT ["./entrypoint.sh"]

# Аргумент по умолчанию для entrypoint (может быть переопределен при запуске контейнера)
CMD ["api"]