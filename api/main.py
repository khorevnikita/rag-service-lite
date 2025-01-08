import logging
import os

import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe import emailpassword, session

from models.base import ModelBase
from routers import api_router
from services.auth.auth_supertokens import override_supertokens_auth
from services.db.pg_database import engine

logging.basicConfig(level=logging.INFO)

# Загрузка переменных окружения из .env файла
load_dotenv()

if os.getenv("SENTRY_API_DNS"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_API_DNS"),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
        environment=os.getenv("SENTRY_ENVIRONMENT"),
    )

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
        session.init(),  # initializes session features
        emailpassword.init(
            override=emailpassword.InputOverrideConfig(apis=override_supertokens_auth)
        ),
    ],
    mode='asgi',  # use wsgi if you are running using gunicorn
)

ModelBase.metadata.create_all(bind=engine)

app = FastAPI(
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",  # Новый путь для openapi.json
    redoc_url=None,  # Отключение ReDoc, если оно вам не нужно
)
app.add_middleware(get_middleware())  # type: ignore

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/api/sentry-debug")
async def trigger_error():
    var = 1 / 0
    return {"error": True, "var": var}
