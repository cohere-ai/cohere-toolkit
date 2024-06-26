import factory

from backend.database_models import Message

from .base import BaseFactory


class MessageFactory(BaseFactory):
    class Meta:
        model = Message

    text = factory.Faker("text")
    tool_plan = factory.Faker("text")
    user_id = factory.Faker("uuid4")
    generation_id = factory.Faker("uuid4")
    conversation_id = factory.Faker("uuid4")
    position = factory.Faker("random_int")
    is_active = factory.Faker("boolean")
    documents = []
    citations = []
    agent = factory.Faker("random_element", elements=("USER", "CHATBOT"))
