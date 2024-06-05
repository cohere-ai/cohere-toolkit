import factory

from backend.database_models.agent import Agent, Deployment, Model

from .base import BaseFactory


class AgentFactory(BaseFactory):
    class Meta:
        model = Agent

    user_id = factory.Faker("uuid4")
    name = factory.Faker("sentence")
    description = factory.Faker("sentence")
    preamble = factory.Faker("sentence")
    version = factory.Faker("random_int")
    temperature = factory.Faker("pyfloat")
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
    model = factory.Faker(
        "random_element",
        elements=(
            Model.COMMAND_R,
            Model.COMMAND_R_PLUS,
            Model.COMMAND_LIGHT,
            Model.COMMAND,
        ),
    )
    deployment = factory.Faker(
        "random_element",
        elements=(
            Deployment.COHERE_PLATFORM,
            Deployment.SAGE_MAKER,
            Deployment.AZURE,
            Deployment.BEDROCK,
        ),
    )


# class ConversationFactory(BaseFactory):
#     class Meta:
#         model = Conversation

#     user_id = factory.Faker("uuid4")
#     description = factory.Faker("sentence")
#     title = factory.Faker("sentence")
#     created_at = factory.Faker("date_time")
#     updated_at = factory.Faker("date_time")
#     text_messages = []
#     files = []
