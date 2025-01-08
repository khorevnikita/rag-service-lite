from typing import Iterable, List, Optional, Tuple

from services.ai_clients.interfaces import AIMessage, IEmbedder, IGenerator, UsageData
from services.ai_clients.openai_service import OpenAIClient
from validators.question_requests import FunctionDefinition


class AIService:
    generators: dict[str, type[IGenerator]] = {
        "openai": OpenAIClient,
    }
    embedders: dict[str, type[IEmbedder]] = {
        "openai": OpenAIClient,
    }

    client: IGenerator | None = None
    embedder: IEmbedder | None = None

    def __init__(self, provider: str, account_id: int):
        if provider in self.generators:
            self.client = self.generators[provider](account_id)
        if provider in self.embedders:
            self.embedder = self.embedders[provider](account_id)

    async def embed(self, text: str) -> Tuple[List[float] | List[int], UsageData]:
        if not self.embedder:
            raise ValueError("Embedder is not initialized")
        return await self.embedder.text_to_vector(text)

    def tokens_count_from_string(self, string: str, model_name: str) -> int:
        if not self.client:
            raise ValueError("AI Client is not initialized")
        return self.client.num_tokens_from_string(string, model_name)

    async def ocr(self, urls: List[str]) -> Tuple[str, UsageData]:
        if not self.client:
            raise ValueError("AI Client is not initialized")
        return await self.client.image_to_text(urls)

    async def speech_to_text(self, urls: List[str]) -> Tuple[str, UsageData]:
        if not self.client:
            raise ValueError("AI Client is not initialized")
        return await self.client.speech_to_text(urls)

    def create_message_stream(
        self,
        system_context: str,
        messages: List[AIMessage],
    ) -> Iterable[Tuple[str, UsageData]]:
        if not self.client:
            raise ValueError("AI Client is not initialized")
        return self.client.create_message_stream(system_context, messages)

    async def create_message(
        self,
        system_context: str,
        messages: List[AIMessage],
        tools: Optional[List[FunctionDefinition]],
    ) -> Tuple[str, List[dict[str, str]], UsageData]:
        if not self.client:
            raise ValueError("AI Client is not initialized")
        return await self.client.create_message(system_context, messages, tools)

    async def extract_meta_from_text(self, text: str) -> Tuple[str, UsageData]:
        if not self.client:
            raise ValueError("AI Client is not initialized")
        return await self.client.extract_meta_from_text(text)
