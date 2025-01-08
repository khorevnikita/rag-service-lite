import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

EMBEDDING_VECTOR_SIZE = 1536  # text-embedding-3-small
# EMBEDDING_VECTOR_SIZE = 3072  # text-embedding-3-large

AI_PROVIDER = "openai"
AI_DEFAULT_MODEL = "gpt-4o-mini"
