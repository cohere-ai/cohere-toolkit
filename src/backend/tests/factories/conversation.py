import factory

from backend.database_models import Conversation, ConversationFileAssociation

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
    agent_id = None


class ConversationFileAssociationFactory(BaseFactory):
    class Meta:
        model = ConversationFileAssociation

    conversation_id = factory.Faker("uuid4")
    user_id = factory.Faker("uuid4")
    file_id = factory.Faker("uuid4")
