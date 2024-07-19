

# need to ignore the yaml files 
# have template files 
# fix the CLI 
# fix docker and deployments 
import os
import yaml

secrets = dict()
configuration = dict()

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "configuration.yaml")) as f:
    secrets.update(yaml.load(f, Loader=yaml.FullLoader))

class DeploymentSettings():
    cohere_platform_config: str = secrets['deployments']['cohere_platform']