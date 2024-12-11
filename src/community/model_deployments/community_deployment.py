from backend.model_deployments.base import BaseDeployment


class CommunityDeployment(BaseDeployment):
    @classmethod
    def is_community(cls):
        return True
