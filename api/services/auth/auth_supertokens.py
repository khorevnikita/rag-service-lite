from datetime import datetime
from typing import List
from uuid import UUID

from supertokens_python.recipe.emailpassword.interfaces import APIInterface, SignUpPostOkResult
from supertokens_python.recipe.emailpassword.types import FormField

from models.account import Account
from models.settings import Settings, SettingsKey
from services.db.pg_database import AsyncSessionLocal


def override_supertokens_auth(
    original_implementation: APIInterface,
):
    original_sign_up_post = original_implementation.sign_up_post

    async def emailpassword_sign_up(
        form_fields: List[FormField],
        *args,  # Для дополнительных аргументов
        **kwargs,  # Для ключевых дополнительных аргументов
    ):
        async with AsyncSessionLocal() as db:
            result = await original_sign_up_post(
                form_fields,
                *args,  # Передача дополнительных аргументов
                **kwargs,  # Передача ключевых аргументов
            )

            if isinstance(result, SignUpPostOkResult):
                password = value_from_form_id(form_fields, 'password')
                if password is None:
                    raise ValueError("Password is required")
                # password = password.encode("utf-8")

                email = value_from_form_id(form_fields, 'email')
                if email is None:
                    raise ValueError("Email is required")

                account = Account(
                    login=email,
                    # password=hashed_password.decode("utf-8"),
                    supertokens_id=UUID(result.user.id),
                    is_active=True,  # todo: make False by default?
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                account.set_password(str(password))
                db.add(account)
                await db.commit()
                await db.refresh(account)

                settings = Settings(account_id=account.id)
                settings.key = SettingsKey.ACCOUNT_API_KEY
                settings.generate_api_key()

                db.add(settings)
                await db.commit()
            return result

    setattr(original_implementation, "sign_up_post", emailpassword_sign_up)
    return original_implementation


def value_from_form_id(form: List[FormField], form_id: str) -> str | None:
    for f in form:
        if f.id == form_id and isinstance(f.value, str):
            return f.value
    return None
