import factory

from backend.models import File

from .base import BaseFactory


class FileFactory(BaseFactory):
    class Meta:
        model = File

    user_id = factory.Faker("uuid4")
    conversation_id = factory.Faker("uuid4")
    file_name = factory.Faker("file_name")
    file_path = factory.Faker("file_path")
