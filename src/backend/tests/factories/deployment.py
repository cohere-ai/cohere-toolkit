import factory

from backend.database_models import Deployment

from .base import BaseFactory


class DeploymentFactory(BaseFactory):
    class Meta:
        model = Deployment

    name = factory.Faker("name")
    description = factory.Faker("text")
    deployment_class_name = "CohereDeployment"
    is_community = False
    default_deployment_config = factory.Faker(
        "pydict", nb_elements=3, variable_nb_elements=True, value_types=["str"]
    )
