from confluent_kafka import Consumer

from config.kafka import KAFKA_URL


def create_consumer(group_name="default_consumer_group") -> Consumer:
    # Создание консьюмера с конфигурациями
    consumer_config = {
        'bootstrap.servers': KAFKA_URL,  # Адреса брокера Kafka
        'group.id': group_name,  # ID группы консьюмера
        'auto.offset.reset': 'earliest',  # Начать чтение с самого начала, если предыдущее смещение неизвестно
        'enable.auto.commit': True,  # Отключаем автоматическое подтверждение смещений
    }
    consumer = Consumer(consumer_config)
    print(f'Consumer created: {consumer_config}')
    return consumer
