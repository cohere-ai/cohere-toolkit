from backend.model_deployments.base import BaseDeployment


class MockDeployment(BaseDeployment):
    event_stream = []
