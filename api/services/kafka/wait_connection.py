import time

from confluent_kafka import KafkaException

from cli import create_topics
from config.kafka import PARTITION_COUNT, REPLICATION_FACTOR


def test_kafka_connection(timeout=5, max_retries=20) -> bool:
    """Пытается подключиться к Kafka и отправить тестовое сообщение.

    :param config: Конфигурация для Producer.
    :param test_topic: Тестовый топик для отправки сообщения.
    :param timeout: Таймаут между попытками подключения.
    :param max_retries: Максимальное количество попыток подключения.
    """
    retries = 0
    while retries < max_retries:
        try:
            create_topics(PARTITION_COUNT, REPLICATION_FACTOR)
            print(f"Успешно подключено к Kafka после {retries} попыток.")
            return True
        except KafkaException as e:
            print(
                f"Ошибка подключения: {e}. Попытка {retries + 1} из {max_retries}. Повтор через {timeout} секунд."
            )
            time.sleep(timeout)
            retries += 1

    print("Не удалось подключиться к Kafka после максимального числа попыток.")
    return False


if __name__ == '__main__':
    # Проверка подключения
    test_kafka_connection()
