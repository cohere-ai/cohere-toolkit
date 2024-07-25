from typing import Optional

from pydantic import BaseModel, Field

from backend.crud import user as user_crud
from backend.database_models.database import DBSessionDep
from backend.schemas.agent import Agent, AgentToolMetadata
from backend.schemas.metrics import MetricsAgent, MetricsMessageType, MetricsUser
from backend.schemas.user import User


class Context(BaseModel):
    request: Optional[dict] = {}
    response: Optional[dict] = {}
    receive: Optional[dict] = {}
    trace_id: str = "default"
    user_id: str = "default"
    event_type: MetricsMessageType = None
    user: Optional[User] = None
    agent: Optional[Agent] = None
    agent_tool_metadata: Optional[AgentToolMetadata] = None
    model: Optional[str] = None
    deployment_name: Optional[str] = None

    # Metrics
    metrics_user: Optional[MetricsUser] = None
    metrics_agent: Optional[MetricsAgent] = None

    def set_request(self, request):
        self.request = request

    def set_response(self, response):
        self.response = response

    def set_receive(self, receive):
        self.receive = receive

    def set_trace_id(self, trace_id: str):
        self.trace_id = trace_id

    def set_user_id(self, user_id: str):
        self.user_id = user_id

    def set_deployment_name(self, deployment_name: str):
        self.deployment_name = deployment_name

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

    def get_metrics_user(self):
        return self.metrics_user

    def get_metrics_agent(self):
        return self.metrics_agent

    def get_model(self):
        return self.model

    def get_deployment_name(self):
        return self.deployment_name

    def with_event_type(self, event_type: MetricsMessageType) -> "Context":
        self.event_type = event_type
        return self

    def with_user(
        self, session: DBSessionDep | None = None, user: User | None = None
    ) -> "Context":
        if not user and not session:
            return self

        if not user:
            user = user_crud.get_user(session, self.user_id)

        if user:
            self.metrics_user = MetricsUser(
                id=user.id, email=user.email, fullname=user.fullname
            )
            self.user = user

        return self

    def with_agent(self, agent: Agent | None) -> "Context":
        self.agent = agent

        if not agent:
            return self

        self.metrics_agent = MetricsAgent(
            id=agent.id,
            version=agent.version,
            name=agent.name,
            temperature=agent.temperature,
            model=agent.model,
            deployment=agent.deployment,
            preamble=agent.preamble,
            description=agent.description,
        )

        return self

    def with_agent_tool_metadata(
        self, agent_tool_metadata: AgentToolMetadata
    ) -> "Context":
        self.agent_tool_metadata = agent_tool_metadata
        return self

    def with_model(self, model: str) -> "Context":
        self.model = model
        return self
