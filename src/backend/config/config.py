

# need to ignore the yaml files 
# have template files 
# fix the CLI 
# fix docker and deployments 
import os
from pydantic import BaseSettings
import yaml

secrets = dict()
configuration = dict()

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "secrets.yaml")) as f:
    secrets.update(yaml.load(f, Loader=yaml.FullLoader))

class Settings(BaseSettings):
    setting_1: str = secrets['setting_1']
    setting_2: str = secrets['setting_2']