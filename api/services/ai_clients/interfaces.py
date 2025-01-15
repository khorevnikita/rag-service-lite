from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Literal, Optional, Tuple

from validators.question_requests import FunctionDefinition

from models.question import AnswerFormat


class UsageData:
    def __init__(self, input_tokens: int, output_tokens: int, model_name: str):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.model_name = model_name


class AIMessage:
    def __init__(self, role: Literal['system', 'user', 'assistant'], content: str):
        self.role = role
        self.content = content


class IEmbedder(ABC):
    """AI клиент для векторизации текста"""

    def __init__(self, account_id: int):
        pass

    @abstractmethod
    async def text_to_vector(self, text: str) -> Tuple[List[float] | List[int], UsageData]:
        """Преобразует текст в векторное представление с помощью выбранной
        модели.

        :param text: Текст для векторизации.
        :return: Кортеж, содержащий векторное представление текста и
            информацию об использовании API.
        """

    @abstractmethod
    def re_rank(self, query: str, documents: List[str]) -> tuple[list[int], list[Any], UsageData]:
        """
        Пересортирует документы по семантическому соответствию запросу
        """


class IGenerator(ABC):
    """AI клиент для генерации текста"""

    def __init__(self, account_id: int):
        """Инициализация клиента с учетной записью пользователя."""

    @abstractmethod
    def num_tokens_from_string(self, string: str, model: str) -> int:
        """Возвращает количество токенов в строке текста для указанной модели.

        :param string: Строка текста.
        :param model: Модель, для которой рассчитывается количество
            токенов.
        :return: Количество токенов в строке.
        """

    @abstractmethod
    async def image_to_text(self, url: List[str]) -> Tuple[str, UsageData]:
        """Преобразует изображение в текст с помощью модели OCR.

        :param url: Список URL-адресов изображений.
        :return: Кортеж, содержащий текст, извлеченный из изображения, и
            информацию об использовании API.
        """

    @abstractmethod
    async def speech_to_text(self, url: List[str]) -> Tuple[str, UsageData]:
        """Преобразует звук в текст с помощью модели Whisper.

        :param url: Список URL-адресов файлов.
        :return: Текст, извлеченный из изображения, и информацию об
            использовании API.
        """

    @abstractmethod
    async def extract_meta_from_text(self, text: str) -> Tuple[str, UsageData]:
        """Вытаскивает из текста авторов, журнал, год, сайт и так далее.

        :param text:
        :return:
        """

    @abstractmethod
    def create_message_stream(
            self,
            system_context: str,
            messages: List[AIMessage],
    ) -> Iterable[Tuple[str, UsageData]]:
        """Задает вопрос к LLM и получает ответ в виде стрима.

        :return:
        """

    @abstractmethod
    async def create_message(
            self,
            system_context: str,
            messages: List[AIMessage],
            tools: Optional[List[FunctionDefinition]],
            answer_format: AnswerFormat,
    ) -> Tuple[str, Optional[str], List[dict[str, str]], UsageData]:
        """Задает вопрос к LLM и получает ответ в виде конечного результата.

        :return:
        """

    def number_tokens_from_messages(self, messages: List[AIMessage], model: str) -> int:
        num = 0
        for message in messages:
            num = num + self.num_tokens_from_string(message.content, model)
        return num
