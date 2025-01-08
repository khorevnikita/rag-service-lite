import logging
from typing import Any, Callable, List

from controllers import ai_controller, document_controller


class Router:
    listening_events: dict[str, Callable[[Any], Any]] = {
        "document_created": document_controller.read,
        "paragraph_created": ai_controller.indexing_paragraph,
        "fill_document_meta": ai_controller.fill_document_meta,
        "hook_answer": ai_controller.hook_answer,
    }

    def __init__(self, key: str, payload: dict[str, Any]) -> None:
        self.key = key
        self.payload = payload

    async def process(self) -> None:
        if self.key in self.listening_events:
            r = self.listening_events[self.key]
            logging.info(f"consumer process: {self.key}")
            await r(self.payload)
        else:
            print("UNKNOWN ROUTE")

    @classmethod
    def get_route_keys(cls) -> List[str]:
        return list(cls.listening_events.keys())
