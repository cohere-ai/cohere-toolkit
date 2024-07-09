from backend.tests.factories.agent import AgentFactory
from backend.tests.factories.agent_tool_metadata import AgentToolMetadataFactory
from backend.tests.factories.blacklist import BlacklistFactory
from backend.tests.factories.citation import CitationFactory
from backend.tests.factories.conversation import ConversationFactory
from backend.tests.factories.document import DocumentFactory
from backend.tests.factories.file import FileFactory
from backend.tests.factories.message import MessageFactory
from backend.tests.factories.organization import OrganizationFactory
from backend.tests.factories.snapshot import (
    SnapshotAccessFactory,
    SnapshotFactory,
    SnapshotLinkFactory,
)
from backend.tests.factories.tool_call import ToolCallFactory
from backend.tests.factories.user import UserFactory

FACTORY_MAPPING = {
    "User": UserFactory,
    "Blacklist": BlacklistFactory,
    "File": FileFactory,
    "Conversation": ConversationFactory,
    "Citation": CitationFactory,
    "Message": MessageFactory,
    "Document": DocumentFactory,
    "Agent": AgentFactory,
    "Organization": OrganizationFactory,
    "ToolCall": ToolCallFactory,
    "Snapshot": SnapshotFactory,
    "SnapshotLink": SnapshotLinkFactory,
    "SnapshotAccess": SnapshotAccessFactory,
    "AgentToolMetadata": AgentToolMetadataFactory,
}


def get_factory(model_name, session=None):
    factory = FACTORY_MAPPING[model_name]
    factory._meta.sqlalchemy_session = session
    return factory
