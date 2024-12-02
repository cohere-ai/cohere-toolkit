import json
import os
from uuid import uuid4

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.config.deployments import ALL_MODEL_DEPLOYMENTS
from backend.database_models import Deployment, Model, Organization
from backend.model_deployments import (
    AzureDeployment,
    BedrockDeployment,
    CohereDeployment,
    SageMakerDeployment,
    SingleContainerDeployment,
)
from community.config.deployments import (
    AVAILABLE_MODEL_DEPLOYMENTS as COMMUNITY_DEPLOYMENTS_SETUP,
)

load_dotenv()

model_deployments = ALL_MODEL_DEPLOYMENTS.copy()
model_deployments.update(COMMUNITY_DEPLOYMENTS_SETUP)

MODELS_NAME_MAPPING = {
    CohereDeployment.name(): {
        "command": {
            "cohere_name": "command",
            "is_default": False,
        },
        "command-nightly": {
            "cohere_name": "command-nightly",
            "is_default": False,
        },
        "command-light": {
            "cohere_name": "command-light",
            "is_default": False,
        },
        "command-light-nightly": {
            "cohere_name": "command-light-nightly",
            "is_default": False,
        },
        "command-r": {
            "cohere_name": "command-r",
            "is_default": False,
        },
        "command-r-plus": {
            "cohere_name": "command-r-plus",
            "is_default": True,
        },
        "c4ai-aya-23": {
            "cohere_name": "c4ai-aya-23",
            "is_default": False,
        },
        "c4ai-aya-23-35b": {
            "cohere_name": "c4ai-aya-23-35b",
            "is_default": False,
        },
        "command-r-08-2024": {
            "cohere_name": "command-r-08-2024",
            "is_default": False,
        },
        "command-r-plus-08-2024": {
            "cohere_name": "command-r-plus-08-2024",
            "is_default": False,
        },
    },
    SingleContainerDeployment.name(): {
        "command": {
            "cohere_name": "command",
            "is_default": False,
        },
        "command-nightly": {
            "cohere_name": "command-nightly",
            "is_default": False,
        },
        "command-light": {
            "cohere_name": "command-light",
            "is_default": False,
        },
        "command-light-nightly": {
            "cohere_name": "command-light-nightly",
            "is_default": False,
        },
        "command-r": {
            "cohere_name": "command-r",
            "is_default": False,
        },
        "command-r-plus": {
            "cohere_name": "command-r-plus",
            "is_default": True,
        },
        "c4ai-aya-23": {
            "cohere_name": "c4ai-aya-23",
            "is_default": False,
        },
        "c4ai-aya-23-35b": {
            "cohere_name": "c4ai-aya-23-35b",
            "is_default": False,
        },
        "command-r-08-2024": {
            "cohere_name": "command-r-08-2024",
            "is_default": False,
        },
        "command-r-plus-08-2024": {
            "cohere_name": "command-r-plus-08-2024",
            "is_default": False,
        },
    },
    SageMakerDeployment.name(): {
        "sagemaker-command": {
            "cohere_name": "command",
            "is_default": True,
        },
    },
    AzureDeployment.name(): {
        "azure-command": {
            "cohere_name": "command-r",
            "is_default": True,
        },
    },
    BedrockDeployment.name(): {
        "cohere.command-r-plus-v1:0": {
            "cohere_name": "command-r-plus",
            "is_default": True,
        },
    },
}


def deployments_models_seed(op):
    """
    Seed default deployments, models, organization, user and agent.
    """
    _ = Session(op.get_bind())

    # Seed default organization
    sql_command = text(
        """
        INSERT INTO organizations (
            id, name, created_at, updated_at
        )
        VALUES (
            :id, :name, now(), now()
        )
        ON CONFLICT (id) DO NOTHING;
    """
    ).bindparams(
        id="default",
        name="Default Organization",
    )
    op.execute(sql_command)

    # Seed deployments and models
    for deployment in MODELS_NAME_MAPPING.keys():
        deployment_id = str(uuid4())
        sql_command = text(
            """
            INSERT INTO deployments (
                id, name, description, default_deployment_config, deployment_class_name, is_community, created_at, updated_at
            )
            VALUES (
                :id, :name, :description, :default_deployment_config, :deployment_class_name, :is_community, now(), now()
            )
            ON CONFLICT (id) DO NOTHING;
        """
        ).bindparams(
            id=deployment_id,
            name=deployment,
            description="",
            default_deployment_config=json.dumps(
                {
                    env_var: os.environ.get(env_var, "")
                    for env_var in model_deployments[deployment].env_vars()
                }
            ),
            deployment_class_name=model_deployments[
                deployment
            ].__name__,
            is_community=deployment in COMMUNITY_DEPLOYMENTS_SETUP,
        )
        op.execute(sql_command)

        for model_name, model_mapping_name in MODELS_NAME_MAPPING[deployment].items():
            model_id = str(uuid4())
            sql_command = text(
                """
                INSERT INTO models (
                    id, name, cohere_name, description, deployment_id, created_at, updated_at
                )
                VALUES (
                    :id, :name, :cohere_name, :description, :deployment_id, now(), now()
                )
                ON CONFLICT (id) DO NOTHING;
            """
            ).bindparams(
                id=model_id,
                name=model_name,
                cohere_name=model_mapping_name["cohere_name"],
                description="",
                deployment_id=deployment_id,
            )
            op.execute(sql_command)


def delete_default_models(op):
    """
    Delete deployments and models.
    """
    session = Session(op.get_bind())
    session.query(Deployment).delete()
    session.query(Model).delete()
    session.query(Organization).filter_by(id="default").delete()
    session.commit()
