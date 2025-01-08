#!/bin/bash

python services/kafka/wait_connection.py

# Запуск в зависимости от режима
case "$MODE" in
  "api")
    alembic upgrade head

    # Запуск веб-сервера
    if [ "$APP_ENV" = 'local' ]; then
      exec uvicorn --reload --host 0.0.0.0 --port 8000 main:app
    else
      exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --timeout 180 main:app
    fi
    ;;
  "consumer")
    if [ "$APP_ENV" = 'local' ]; then
      exec watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- python main_queue.py
    else
      python main_queue.py
    fi
    ;;
  *)
    echo "Unknown mode: $MODE"
    exit 1
    ;;
esac