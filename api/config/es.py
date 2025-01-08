import os

host = "http://elasticsearch:9200"  # Пример URL для Elasticsearch
index = os.getenv("ES_INDEX_NAME", 'paragraphs')  # Индекс Elasticsearch
document_limit = int(os.getenv("ES_DOCUMENT_LIMIT", 64))
