from community.model_deployments.community_deployment import CommunityDeployment

# Add the below for local model deployments
# from community.model_deployments.local_model import LocalModelDeployment

AVAILABLE_MODEL_DEPLOYMENTS = { d.name(): d for d in CommunityDeployment.__subclasses__() }
