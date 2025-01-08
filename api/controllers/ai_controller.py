from models.document import Document
from models.document import StatusEnum as DocumentStatus
from models.paragraph import Paragraph
from models.paragraph import StatusEnum as ParagraphStatus
from services import s3
from services.db.pg_database import SessionLocal


#####################################################
# Индексация параграфа, сохранение в Elastic search #
#####################################################
async def indexing_paragraph(payload):
    # Получаем данные из БД
    with SessionLocal() as db_session:
        paragraph = db_session.get(Paragraph, payload["id"])
        if not paragraph:
            # Удалили?
            return

        if not paragraph.content_url:
            # Параграф без контента
            return
        paragraph.status = ParagraphStatus.INDEXING
        db_session.commit()

        vector = await paragraph.make_embedding(db_session)
        if not vector:
            return
        paragraph.save_to_es(db_session, vector, s3.read_content(paragraph.content_url))

        paragraph = db_session.get(Paragraph, payload["id"])
        if not paragraph:
            return
        paragraph.status = ParagraphStatus.COMPLETED
        db_session.commit()

        paragraphs_remain_count = (
            db_session.query(Paragraph)
            .filter(
                Paragraph.status != ParagraphStatus.COMPLETED,
                Paragraph.document_id == paragraph.document_id,
            )
            .count()
        )

        if paragraphs_remain_count == 0:
            document = db_session.get(Document, paragraph.document_id)
            if not document:
                return
            document.status = DocumentStatus.READ
            db_session.commit()


async def fill_document_meta(payload):
    with SessionLocal() as db:
        document = db.get(Document, payload["id"])
        if not document:
            return
        await document.set_meta(db)


async def hook_answer(payload):
    # todo: отправлять ответ по хуку
    pass
