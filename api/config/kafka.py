import os
from dotenv import load_dotenv

load_dotenv()
KAFKA_URL = os.getenv("KAFKA_URL")
PARTITION_COUNT = 5
REPLICATION_FACTOR = 1
