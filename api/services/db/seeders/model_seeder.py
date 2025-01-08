from typing import Any, Dict, List

from models.model import Model
from services.db.pg_database import SessionLocal


def seed() -> None:
    model_list: List[Dict[str, Any]] = [
        {
            "name": "text-embedding-3-small",
            "input": 0.1,
            "output": 0.1,
        },
        {
            "name": "text-embedding-3-large",
            "input": 0.1,
            "output": 0.1,
        },
        {
            "name": "gpt-4o",
            "input": 2.5,
            "output": 10,
        },
        {
            "name": "gpt-4o-mini",
            "input": 0.15,
            "output": 0.6,
        },
        {
            "name": "whisper-1",
            "input": 0.006,
            "output": 0,
        },
    ]

    with SessionLocal() as db:
        for model in model_list:
            existing_model = db.query(Model).filter_by(base_model_name=model["name"]).first()
            if existing_model:
                existing_model.input = model["input"]
                existing_model.output = model["output"]
            else:
                new_model = Model(
                    base_model_name=model["name"],
                    input=model["input"],
                    output=model["output"],
                )
                db.add(new_model)
        db.commit()


if __name__ == '__main__':
    seed()
