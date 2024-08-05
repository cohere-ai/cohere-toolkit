import json
import os

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.config.deployments import ALL_MODEL_DEPLOYMENTS, ModelDeploymentName
from backend.database_models import (
    Agent,
    AgentDeploymentModel,
    Deployment,
    Model,
    Organization,
    User,
)
from backend.schemas.agent import DEFAULT_AGENT_ID, DEFAULT_AGENT_NAME
from community.config.deployments import (
    AVAILABLE_MODEL_DEPLOYMENTS as COMMUNITY_DEPLOYMENTS_SETUP,
)

load_dotenv()

model_deployments = ALL_MODEL_DEPLOYMENTS.copy()
model_deployments.update(COMMUNITY_DEPLOYMENTS_SETUP)

MODELS_NAME_MAPPING = {
    ModelDeploymentName.CoherePlatform: {
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
    },
    ModelDeploymentName.SingleContainer: {
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
    },
    ModelDeploymentName.SageMaker: {
        "sagemaker-command": {
            "cohere_name": "command",
            "is_default": True,
        },
    },
    ModelDeploymentName.Azure: {
        "azure-command": {
            "cohere_name": "command-r",
            "is_default": True,
        },
    },
    ModelDeploymentName.Bedrock: {
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
    session = Session(op.get_bind())

    default_user = session.query(User).filter_by(id="user-id").first()
    default_organization = Organization(
        name="Default Organization",
        id="default",
    )
    session.add(default_organization)
    session.commit()
    default_organization.users.append(default_user)
    session.commit()
    tools = [
        "web_search",
        "search_file",
        "read_document",
        "toolkit_python_interpreter",
        "toolkit_calculator",
        "wikipedia",
        "google_drive",
        "arxiv",
        "example_connector",
        "pub_med",
        "file_reader_llamaindex",
        "wolfram_alpha",
        "clinical_trials",
    ]
    tools_json = json.dumps(tools)
    sql_command = text(
        """
        INSERT INTO agents (
            id, version, name, description, preamble, temperature, tools, 
            user_id, organization_id, created_at, updated_at
        )
        VALUES (
            :id, 1, :name, 'Default agent', '', 0.3, :tools, :user_id, 
            :organization_id, now(), now()
        )
        ON CONFLICT (id) DO NOTHING;
    """
    ).bindparams(
        id=DEFAULT_AGENT_ID,
        name=DEFAULT_AGENT_NAME,
        tools=tools_json,
        user_id=default_user.id,
        organization_id=default_organization.id,
    )

    op.execute(sql_command)

    # Seed deployments and models
    for deployment in MODELS_NAME_MAPPING.keys():
        new_deployment = Deployment(
            name=deployment,
            default_deployment_config={
                env_var: os.environ.get(env_var, "")
                for env_var in model_deployments[deployment].env_vars
            },
            deployment_class_name=model_deployments[
                deployment
            ].deployment_class.__name__,
            is_community=deployment in COMMUNITY_DEPLOYMENTS_SETUP,
        )
        session.add(new_deployment)
        session.commit()
        is_default_for_agent = False
        for model_name, model_mapping_name in MODELS_NAME_MAPPING[deployment].items():
            new_model = Model(
                name=model_name,
                cohere_name=model_mapping_name["cohere_name"],
                deployment_id=new_deployment.id,
            )
            session.add(new_model)
            session.commit()
            if model_mapping_name["is_default"]:
                model_to_agent_id = new_model.id
                is_default_for_agent = True

        agent_deployment_association = AgentDeploymentModel(
            deployment_id=new_deployment.id,
            agent_id=DEFAULT_AGENT_ID,
            model_id=model_to_agent_id,
            deployment_config={
                env_var: os.environ.get(env_var, "")
                for env_var in model_deployments[deployment].env_vars
            },
            is_default_deployment=new_deployment.name
            == ModelDeploymentName.CoherePlatform,
            is_default_model=is_default_for_agent,
        )
        session.add(agent_deployment_association)
        session.commit()


def delete_default_models(op):
    """
    Delete deployments and models.
    """
    session = Session(op.get_bind())
    session.query(Deployment).delete()
    session.query(Model).delete()
    session.query(Organization).filter_by(id="default").delete()
    session.query(AgentDeploymentModel).delete()
    session.commit()
