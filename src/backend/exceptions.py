class ToolkitException(Exception):
    """
    Base class for all toolkit exceptions.
    """

class DeploymentNotFoundError(ToolkitException):
    def __init__(self, deployment_id: str):
        super(DeploymentNotFoundError, self).__init__(f"Deployment {deployment_id} not found")
        self.deployment_id = deployment_id

class NoAvailableDeploymentsError(ToolkitException):
    def __init__(self):
        super(NoAvailableDeploymentsError, self).__init__("No deployments have been configured. Have the appropriate config values been added to configuration.yaml or secrets.yaml?")
