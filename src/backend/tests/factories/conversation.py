import factory

from backend.database_models import Conversation

from .base import BaseFactory


class ConversationFactory(BaseFactory):
    class Meta:
        model = Conversation

    user_id = factory.Faker("uuid4")
    description = factory.Faker("sentence")
    title = factory.Faker("sentence")
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
    text_messages = []
    files = []
    agent_id = None
