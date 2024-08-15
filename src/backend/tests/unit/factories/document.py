import factory

from backend.database_models import Document

from .base import BaseFactory


class DocumentFactory(BaseFactory):
    class Meta:
        model = Document

    user_id = factory.Faker("uuid4")
    title = factory.Faker("sentence")
    url = factory.Faker("url")
    conversation_id = factory.Faker("uuid4")
    message_id = factory.Faker("uuid4")
    document_id = factory.Faker("uuid4")
    text = factory.Faker("text")
