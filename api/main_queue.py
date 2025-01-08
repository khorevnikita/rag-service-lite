import asyncio
import json
import logging
import os
import sys

import sentry_sdk
from confluent_kafka import Consumer, KafkaError, KafkaException
from dotenv import load_dotenv

from services.kafka.consumer import create_consumer
from services.kafka.router import Router

load_dotenv()

if os.getenv("SENTRY_API_DNS"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_API_DNS"),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
        environment=os.getenv("SENTRY_ENVIRONMENT"),
    )

logging.basicConfig(level=logging.INFO)


async def consume_messages(c: Consumer):
    try:
        # Подписка на тему
        route_keys = Router.get_route_keys()
        c.subscribe(route_keys)

        while True:
            # Пытаемся получить новые сообщения
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:  # pylint: disable=W0212
                    # End of partition event
                    sys.stderr.write(
                        f'{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}\n'
                    )
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # Печатаем сообщение
                message = msg.value().decode("utf-8")
                payload = json.loads(message)
                topic = msg.topic()
                print(f'Received message. {topic}: {message}')
                if topic is None:
                    print('Message without a topic')
                    return

                r = Router(topic, payload)
                await r.process()

    finally:
        # Закрываем консьюмер, освобождаем ресурсы
        c.close()


if __name__ == '__main__':

    consumer = create_consumer("core")
    try:
        # Начинаем потребление сообщений
        asyncio.run(consume_messages(consumer))
    except KeyboardInterrupt:
        sys.stderr.write('Aborted by user\n')
    except KafkaException as e:
        sys.stderr.write(f'Kafka exception: {e}\n')
    finally:
        consumer.close()
