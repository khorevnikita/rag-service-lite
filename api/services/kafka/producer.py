import json
from typing import Any, Dict

from confluent_kafka import Message, Producer

from config.kafka import KAFKA_URL


def delivery_report(err: Any, msg: Message) -> None:
    """Callback функция для обработки результата доставки."""
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


# Создание глобального producer для использования в приложении
def create_producer(client_id: str) -> Producer:
    """Создаёт Kafka Producer с заданным client_id."""
    producer_config = {
        'bootstrap.servers': KAFKA_URL,  # Адрес Kafka внутри вашей сети Docker
        'client.id': client_id,
    }

    producer = Producer(producer_config)
    return producer


def send_message(client_id: str, topic: str, key: str, message: Dict[str, Any]) -> None:
    """Отправляет сообщение в Kafka."""
    producer = create_producer(client_id=client_id)
    producer.produce(
        topic=topic,  # Название Kafka топика
        key=key,  # Ключ сообщения
        value=json.dumps(message).encode('utf-8'),  # Сообщение сериализовано в JSON
        callback=delivery_report,  # Callback функция
    )
    producer.poll(0)  # Обработка доставки
    producer.flush()  # Ожидание завершения доставки
