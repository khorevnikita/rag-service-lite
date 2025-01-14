import io
import logging
import os
from typing import Any, Iterable, List, Literal, Optional, Tuple

import requests
import tiktoken
from openai import AsyncClient, OpenAI
from openai.types.chat.chat_completion_assistant_message_param import (
    ChatCompletionAssistantMessageParam,
)
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_system_message_param import ChatCompletionSystemMessageParam
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam
from pydub import AudioSegment

from config import ai
from models.settings import get_generative_model, get_openai_key, get_temperature
from services.ai_clients.interfaces import AIMessage, IEmbedder, IGenerator, UsageData
from validators.question_requests import FunctionDefinition

SYSTEM_ROLE: Literal['system'] = 'system'
USER_ROLE: Literal['user'] = 'user'
ASSISTANT_ROLE: Literal['assistant'] = 'assistant'


class OpenAIClient(IGenerator, IEmbedder):
    general_model = ai.AI_DEFAULT_MODEL
    temperature = 0.1

    def __init__(self, account_id: int):
        super().__init__(account_id)
        self.account_id = account_id
        self.client = AsyncClient(api_key=get_openai_key(account_id))
        self.general_model = get_generative_model(self.account_id)
        self.temperature = get_temperature(self.account_id)

    async def text_to_vector(self, text: str) -> Tuple[List[float], UsageData]:
        response = await self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small",  # Или другая модель по вашему выбору
        )
        embedding = response.data[0].embedding
        usage = response.usage
        return embedding, UsageData(
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.total_tokens - usage.prompt_tokens,
            model_name="text-embedding-3-small",
        )

    def num_tokens_from_string(self, string: str, model: str) -> int:
        """Returns the number of tokens in a text string."""

        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            self.general_model,
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            print(
                "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613."
            )
            return self.num_tokens_from_string(string, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_string(string, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )

        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        num_tokens = len(encoding.encode(string)) + tokens_per_message + tokens_per_name
        return num_tokens

    async def image_to_text(self, url: List[str]) -> Tuple[str, UsageData]:
        """
        Распознает изображение в текст (OCR)
        """
        # Формируем сообщения с изображениями
        file_message = "\n".join([f"Image URL: {f}" for f in url])

        system_message: ChatCompletionSystemMessageParam = {
            "role": SYSTEM_ROLE,
            "content": "You are an OCR system. Just try to convert image to text and nothing else.",
        }

        user_message: ChatCompletionUserMessageParam = {
            "role": "user",
            "content": f"Convert the following images to text:\n{file_message}",
        }

        messages: Iterable[ChatCompletionMessageParam] = [
            system_message,
            user_message,
        ]

        # Отправляем запрос в API
        response = await self.client.chat.completions.create(
            model=self.general_model,
            messages=messages,
        )
        result = response.choices[0].message
        usage = response.usage

        # Возвращаем результат
        return result.content or "", UsageData(
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            model_name=self.general_model,
        )

    def read_audio(self, file_path):
        with open(file_path, "rb") as f:
            return f.read()

    async def speech_to_text(self, urls: List[str]) -> Tuple[str, UsageData]:
        text = ""
        total_duration = 0.0
        for remote_url in urls:
            logging.info(f"Processing URL: {remote_url}")

            try:
                # Загружаем файл в память
                response = requests.get(remote_url, stream=True)
                response.raise_for_status()

                # Читаем аудио в буфер
                audio_data = io.BytesIO(response.content)

                file_extension = os.path.splitext(remote_url.split("?")[0])[1].lower().strip(".")
                if file_extension not in ["mp3", "wav", "ogg", "flac"]:
                    raise ValueError(f"Unsupported file extension: {file_extension}")

                # Конвертируем в совместимый формат (Flac)
                audio_segment = AudioSegment.from_file(audio_data, format=file_extension)
                audio_duration = len(audio_segment) / 1000
                logging.info(f"Original audio duration: {audio_duration} seconds")

                # Экспортируем в Flac
                buffer = io.BytesIO()
                buffer.name = f"processed_audio.{file_extension}"
                audio_segment.export(buffer, format=file_extension)
                buffer.seek(0)

                # Отправляем в Whisper API
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1", file=buffer
                )
                logging.info(f"Transcription result: {transcript}")

                # Сохраняем текст
                text += transcript.text
                total_duration += audio_duration

            except Exception as e:
                logging.error(f"Error processing URL {remote_url}: {e}")

        return text, UsageData(
            input_tokens=round(total_duration), output_tokens=0, model_name="whisper-1"
        )

    async def extract_meta_from_text(self, text: str) -> Tuple[str, UsageData]:

        system_message: ChatCompletionSystemMessageParam = ChatCompletionSystemMessageParam(
            role=SYSTEM_ROLE,
            content="You are a document analyser. Your target is to detect and collect meta information about the article such as authors, website, address, year, magazine, etc. Write down only meta information.",
        )

        user_message: ChatCompletionUserMessageParam = ChatCompletionUserMessageParam(
            role=USER_ROLE,
            content=f"What is the source of the following document:\n{text}\n",
        )

        completion = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_message, user_message],
        )

        meta = completion.choices[0].message.content
        usage = completion.usage
        return meta or "", UsageData(
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            model_name="gpt-4o-mini",
        )

    def set_tools(self, tools: Optional[List[FunctionDefinition]]):
        if not tools:
            return None

        return [
            {
                "type": "function",
                "function": {
                    "name": x.name,
                    "description": x.description,
                    "parameters": x.input_schema.to_dict() if x.input_schema else None,
                },
            }
            for x in tools
        ]

    def create_message_stream(
        self,
        system_context: str,
        messages: List[AIMessage],
    ) -> Iterable[Tuple[str, UsageData]]:

        input_tokens = self.number_tokens_from_messages(messages, self.general_model)

        usage = UsageData(input_tokens=input_tokens, output_tokens=0, model_name=self.general_model)

        client = OpenAI(api_key=get_openai_key(self.account_id))

        stream = client.chat.completions.create(
            model=self.general_model,
            messages=parse_ai_messages_to_openai(system_context, messages),
            temperature=self.temperature,
            stream=True,
        )

        answer = ""
        for message in stream:
            delta = message.choices[0].delta
            if delta.content:
                answer += delta.content
                yield delta.content, usage
            else:
                usage.output_tokens = self.num_tokens_from_string(answer, self.general_model)
                yield "", usage

    async def create_message(
        self,
        system_context: str,
        messages: List[AIMessage],
        tools: Optional[List[FunctionDefinition]],
    ) -> Tuple[str, List[dict[str, str]], UsageData]:

        completion = await self.client.chat.completions.create(
            temperature=self.temperature,
            model=self.general_model,
            messages=parse_ai_messages_to_openai(system_context, messages),
            tools=self.set_tools(tools),
        )

        answer = completion.choices[0].message
        usage = completion.usage

        called_tools = []
        if answer.tool_calls:
            called_tools = [
                {"function_name": t.function.name, "arguments": t.function.arguments}
                for t in answer.tool_calls
            ]

        return (
            answer.content or "",
            called_tools,
            UsageData(
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                model_name=self.general_model,
            ),
        )

    def re_rank(self, query: str, documents: List[str]) -> Tuple[List[int], list[Any], UsageData]:
        return (
            list(range(len(documents))),  # Индексы документов
            [],  # Пустой список как заглушка
            UsageData(  # UsageData с нулевыми значениями
                input_tokens=0,
                output_tokens=0,
                model_name="placeholder_model",
            ),
        )


def parse_ai_messages_to_openai(
    ctx: str, messages: List[AIMessage]
) -> List[ChatCompletionMessageParam]:
    system_message: ChatCompletionSystemMessageParam = {"role": SYSTEM_ROLE, "content": ctx}
    ai_messages: List[ChatCompletionMessageParam] = []
    for m in messages:
        if m.role == USER_ROLE:
            ai_messages.append(ChatCompletionUserMessageParam(role=USER_ROLE, content=m.content))
        if m.role == ASSISTANT_ROLE:
            ai_messages.append(
                ChatCompletionAssistantMessageParam(role=ASSISTANT_ROLE, content=m.content)
            )

    msgs: List[ChatCompletionMessageParam] = [
        system_message,
        *ai_messages,
    ]
    return msgs
