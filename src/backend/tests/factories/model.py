import factory

from backend.database_models import Model
from backend.tests.factories.base import BaseFactory
from backend.tests.factories.deployment import DeploymentFactory


class ModelFactory(BaseFactory):
    class Meta:
        model = Model

    deployment = factory.SubFactory(DeploymentFactory)
    deployment_id = factory.SelfAttribute("deployment.id")
    name = factory.Faker("name")
    cohere_name = factory.Faker("name")
    description = factory.Faker("text")
