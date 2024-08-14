from enum import StrEnum

from community.model_deployments import Deployment
from community.model_deployments.hugging_face import HuggingFaceDeployment

# Add the below for local model deployments
# from community.model_deployments.local_model import LocalModelDeployment


class ModelDeploymentName(StrEnum):
    HuggingFace = "HuggingFace"
    LocalModel = "LocalModel"


AVAILABLE_MODEL_DEPLOYMENTS = {
    # ModelDeploymentName.HuggingFace: Deployment(
    #     id = "hugging_face",
    #     name=ModelDeploymentName.HuggingFace,
    #     deployment_class=HuggingFaceDeployment,
    #     models=HuggingFaceDeployment.list_models(),
    #     is_available=HuggingFaceDeployment.is_available(),
    #     env_vars=[],
    # ),
    # # Add the below for local model deployments
    # ModelDeploymentName.LocalModel: Deployment(
    #     id = "local_model",
    #     name=ModelDeploymentName.LocalModel,
    #     deployment_class=LocalModelDeployment,
    #     models=LocalModelDeployment.list_models(),
    #     is_available=LocalModelDeployment.is_available(),
    #     env_vars=[],
    #     kwargs={
    #         "model_path": "path/to/model",  # Note that the model needs to be in the src directory
    #     },
    # ),
}
