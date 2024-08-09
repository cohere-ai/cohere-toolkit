from backend.tests.unit.factories.agent import AgentFactory
from backend.tests.unit.factories.agent_deployment_model import (
    AgentDeploymentModelFactory,
)
from backend.tests.unit.factories.agent_tool_metadata import AgentToolMetadataFactory
from backend.tests.unit.factories.base import BaseFactory
from backend.tests.unit.factories.blacklist import BlacklistFactory
from backend.tests.unit.factories.citation import CitationFactory
from backend.tests.unit.factories.citation_documents import CitationDocumentsFactory
from backend.tests.unit.factories.conversation import (
    ConversationFactory,
    ConversationFileAssociationFactory,
)
from backend.tests.unit.factories.deployment import DeploymentFactory
from backend.tests.unit.factories.document import DocumentFactory
from backend.tests.unit.factories.file import FileFactory
from backend.tests.unit.factories.message import (
    MessageFactory,
    MessageFileAssociationFactory,
)
from backend.tests.unit.factories.model import ModelFactory
from backend.tests.unit.factories.organization import OrganizationFactory
from backend.tests.unit.factories.snapshot import (
    SnapshotAccessFactory,
    SnapshotFactory,
    SnapshotLinkFactory,
)
from backend.tests.unit.factories.tool_call import ToolCallFactory
from backend.tests.unit.factories.user import UserFactory

FACTORY_MAPPING = {
    "User": UserFactory,
    "Blacklist": BlacklistFactory,
    "File": FileFactory,
    "Conversation": ConversationFactory,
    "Citation": CitationFactory,
    "CitationDocuments": CitationDocumentsFactory,
    "Message": MessageFactory,
    "Document": DocumentFactory,
    "Agent": AgentFactory,
    "Organization": OrganizationFactory,
    "ToolCall": ToolCallFactory,
    "Snapshot": SnapshotFactory,
    "SnapshotLink": SnapshotLinkFactory,
    "SnapshotAccess": SnapshotAccessFactory,
    "AgentToolMetadata": AgentToolMetadataFactory,
    "Model": ModelFactory,
    "Deployment": DeploymentFactory,
    "AgentDeploymentModel": AgentDeploymentModelFactory,
    "ConversationFileAssociation": ConversationFileAssociationFactory,
    "MessageFileAssociation": MessageFileAssociationFactory,
}


def get_factory(model_name, session=None):
    factory = FACTORY_MAPPING[model_name]
    factory._meta.sqlalchemy_session = session
    return factory
