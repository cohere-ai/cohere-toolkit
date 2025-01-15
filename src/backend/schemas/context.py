from typing import Any, Optional, Self

from pydantic import BaseModel

from backend.crud import organization as organization_crud
from backend.crud import user as user_crud
from backend.database_models.database import DBSessionDep
from backend.schemas import Organization
from backend.schemas.agent import Agent, AgentToolMetadata
from backend.schemas.user import User
from backend.services.logger.utils import LoggerFactory
from backend.services.utils import get_deployment_config


class Context(BaseModel):
    """
    Context for a request
    """
    request: Optional[dict] = {}
    response: Optional[dict] = {}
    receive: Optional[dict] = {}
    trace_id: str = "default"
    user_id: str = "default"
    user: Optional[User] = None
    agent: Optional[Agent] = None
    agent_tool_metadata: Optional[AgentToolMetadata] = None
    model: Optional[str] = None
    deployment_name: Optional[str] = None
    deployment_config: Optional[dict] = None
    conversation_id: Optional[str] = None
    agent_id: Optional[str] = None
    stream_start_ms: Optional[float] = None
    logger: Optional[Any] = None
    organization_id: Optional[str] = None
    organization: Optional[Organization] = None
    use_global_filtering: Optional[bool] = False

    def __init__(self):
        super().__init__()
        self.with_logger()

    def set_request(self, request):
        self.request = request

    def set_response(self, response):
        self.response = response

    def set_receive(self, receive):
        self.receive = receive

    def with_logger(self):
        if self.logger is not None:
            return self

        logger = LoggerFactory().get_logger()
        logger.bind(trace_id=self.trace_id, user_id=self.user_id)
        self.logger = logger
        return self

    def with_trace_id(self, trace_id: str):
        self.trace_id = trace_id

    def with_user_id(self, user_id: str):
        self.user_id = user_id

    def with_deployment_name(self, deployment_name: str):
        self.deployment_name = deployment_name

    def with_user(
        self, session: DBSessionDep | None = None, user: User | None = None
    ) -> Self:
        if not user and not session:
            return self

        if not user:
            user = user_crud.get_user(session, self.user_id)
            user = User.model_validate(user)

        if user:
            self.user = user

        return self

    def with_agent(self, agent: Agent | None) -> Self:
        self.agent = agent
        return self

    def with_agent_tool_metadata(
        self, agent_tool_metadata: AgentToolMetadata
    ) -> Self:
        self.agent_tool_metadata = agent_tool_metadata
        return self

    def with_model(self, model: str) -> Self:
        self.model = model
        return self

    def with_deployment_config(self, deployment_config=None) -> Self:
        if deployment_config:
            self.deployment_config = deployment_config
        else:
            self.deployment_config = get_deployment_config(self.request)
        return self

    def with_conversation_id(self, conversation_id: str) -> Self:
        self.conversation_id = conversation_id
        return self

    def with_stream_start_ms(self, now_ms: float) -> Self:
        self.stream_start_ms = now_ms

    def with_agent_id(self, agent_id: str) -> Self:
        if not agent_id:
            return self

        self.agent_id = agent_id
        return self

    def with_organization_id(self, organization_id: str) -> Self:
        self.organization_id = organization_id
        return self

    def with_organization(
        self,
        session: DBSessionDep | None = None,
        organization: Organization | None = None,
    ) -> Self:
        if not organization and not session:
            return self

        if not organization:
            organization = organization_crud.get_organization(
                session, self.organization_id
            )
            organization = (
                Organization.model_validate(organization) if organization else None
            )

        if organization:
            self.organization = organization

        return self

    def with_global_filtering(self) -> Self:
        self.use_global_filtering = True
        return self

    def without_global_filtering(self) -> Self:
        self.use_global_filtering = False
        return self

    def get_organization(self):
        return self.organization

    def get_stream_start_ms(self):
        return self.stream_start_ms

    def get_request(self):
        return self.request

    def get_response(self):
        return self.response

    def get_receive(self):
        return self.receive

    def get_trace_id(self):
        return self.trace_id

    def get_user_id(self):
        return self.user_id

    def get_event_type(self):
        return self.event_type

    def get_model(self):
        return self.model

    def get_deployment_name(self):
        return self.deployment_name

    def get_model_config(self):
        return self.model_config

    def get_conversation_id(self):
        return self.conversation_id

    def get_agent_id(self):
        return self.agent_id

    def get_logger(self) -> Any:
        return self.logger

    def get_agent_tool_metadata(self):
        return self.agent_tool_metadata
