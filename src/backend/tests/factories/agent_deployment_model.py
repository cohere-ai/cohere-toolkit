import factory

from backend.database_models.agent import AgentDeploymentModel
from backend.tests.factories.agent import AgentFactory
from backend.tests.factories.base import BaseFactory
from backend.tests.factories.deployment import DeploymentFactory
from backend.tests.factories.model import ModelFactory


class AgentDeploymentModelFactory(BaseFactory):

    class Meta:
        model = AgentDeploymentModel

    agent = factory.SubFactory(AgentFactory)
    deployment = factory.SubFactory(DeploymentFactory)
    model = factory.SubFactory(ModelFactory)
    agent_id = factory.SelfAttribute("agent.id")
    deployment_id = factory.SelfAttribute("deployment.id")
    model_id = factory.SelfAttribute("model.id")
    deployment_config: factory.Faker(
        "pydict", nb_elements=3, variable_nb_elements=True, value_types=["str"]
    )
    is_default_deployment: False
    is_default_model: False
