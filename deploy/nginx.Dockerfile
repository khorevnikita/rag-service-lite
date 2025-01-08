# Используем официальный образ NGINX
FROM nginx:latest

# Установка apache2-utils для использования htpasswd
RUN apt-get update && \
    apt-get install -y apache2-utils

# Копирование вашего файла конфигурации NGINX, если он у вас есть
COPY nginx.conf /etc/nginx/nginx.conf

# Остальные команды для настройки вашего образа
