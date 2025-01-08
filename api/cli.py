import os
import random
import string

import click
from confluent_kafka.admin import AdminClient, NewTopic
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.recipe import emailpassword, session

from config import ai as ai_config
from config import es as es_config
from config import kafka
from services.kafka.router import Router

load_dotenv()

init(
    app_info=InputAppInfo(
        app_name="rag-service",
        api_domain=os.getenv("APP_URL", ""),
        website_domain=os.getenv("APP_URL"),
        api_base_path="/api/auth",
        website_base_path="/auth",
    ),
    supertokens_config=SupertokensConfig(
        connection_uri="http://supertokens:3567",
    ),
    framework='fastapi',
    recipe_list=[
        session.init(),
        emailpassword.init(),
    ],
    mode='asgi',  # use wsgi if you are running using gunicorn
)


def generate_random_password(length=16):
    """Генерация случайного пароля"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(characters, k=length))


def create_topics(num_partitions: int, replication_factor: int) -> None:
    # Создаем AdminClient с использованием настроек вашего Kafka кластера
    admin_client = AdminClient({'bootstrap.servers': kafka.KAFKA_URL})

    route_keys = Router.get_route_keys()
    new_topics = [
        NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor)
        for topic in route_keys
    ]

    # Создаем топики
    fs = admin_client.create_topics(new_topics)

    # Проверяем результат создания каждого топика
    for topic, f in fs.items():
        try:
            f.result()  # Блокирующий вызов
            print(f"Topic {topic} created")
        except Exception as e:
            print(f"Failed to create topic {topic}: {e}")


@click.group()
def cli():
    pass


@cli.command()
@click.option('--name', help='Имя индекса')
def create_index(name):
    # Создание экземпляра клиента Elasticsearch
    es = Elasticsearch([es_config.host])

    # Определение маппинга для индекса
    mapping = {
        "mappings": {
            "properties": {
                "account_id": {"type": "keyword"},  # Для точного совпадения
                "content_vector": {
                    "type": "dense_vector",
                    "dims": ai_config.EMBEDDING_VECTOR_SIZE,  # Укажите размерность вектора, например 768
                    "index": True,  # Включить индексацию для поиска kNN
                    "similarity": "cosine",  # Тип метрики (L2, dot_product и т.д.)
                },
                "content": {"type": "text"},  # Если вы также хотите искать по тексту
            }
        },
        # "settings": {
        #    "index": {
        #        "knn": True  # Включение поддержки kNN для dense_vector
        #    }
        # }
    }
    # Создание индекса с заданным маппингом
    response = es.indices.create(index=name, body=mapping)

    # Вывод ответа сервера
    print(response)


if __name__ == '__main__':
    cli()
