# Этап 1: Сборка приложения
FROM node:22-slim as base

WORKDIR /app

# Копирование файлов `package.json` и `package-lock.json` (или `yarn.lock`)
COPY package*.json ./

# Установка зависимостей проекта
RUN npm ci

# Копирование исходного кода проекта
COPY . .


FROM base as local
EXPOSE 80
CMD ["npx","vite","--port=80","--host"]

FROM base as build-stage
# Сборка приложения
RUN npm run build

# Этап 2: Настройка сервера Nginx для размещения приложения
FROM nginx:stable-alpine as production

# Копирование собранного приложения из предыдущего этапа
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Копирование конфигурации Nginx (если требуется)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открытие порта 80 для входящих подключений
EXPOSE 80

# Запуск Nginx при запуске контейнера
CMD ["nginx", "-g", "daemon off;"]
