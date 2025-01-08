from fastapi import APIRouter

from . import (
    auth,
    conversation,
    dashboard,
    documents,
    keywords,
    questions,
    settings,
    storage,
    usage,
)

api_router = APIRouter(prefix='/api')

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(documents.router, tags=["documents"])
api_router.include_router(storage.router, tags=["storage"])
api_router.include_router(questions.router, tags=["questions"])
api_router.include_router(usage.router, tags=["usage"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(settings.router, tags=["settings"])
api_router.include_router(keywords.router, tags=["keywords"])
api_router.include_router(conversation.router, tags=["conversation"])
