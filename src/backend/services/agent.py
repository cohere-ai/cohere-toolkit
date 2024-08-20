import pickle

from fastapi import HTTPException

from backend.crud import agent as agent_crud
from backend.crud import agent_tool_metadata as agent_tool_metadata_crud
from backend.database_models.agent import Agent, AgentToolMetadata
from backend.database_models.agent_task import SyncCeleryTaskMeta
from backend.database_models.database import DBSessionDep
from backend.schemas.agent import AgentTaskResponse


def validate_agent_exists(session: DBSessionDep, agent_id: str, user_id: str) -> Agent:
    agent = agent_crud.get_agent_by_id(session, agent_id, user_id)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent with ID {agent_id} not found.",
        )

    return agent


def validate_agent_tool_metadata_exists(
    session: DBSessionDep, agent_tool_metadata_id: str
) -> AgentToolMetadata:
    agent_tool_metadata = agent_tool_metadata_crud.get_agent_tool_metadata_by_id(
        session, agent_tool_metadata_id
    )

    if not agent_tool_metadata:
        raise HTTPException(
            status_code=404,
            detail=f"Agent tool metadata with ID {agent_tool_metadata_id} not found.",
        )

    return agent_tool_metadata


def raise_db_error(e: Exception, type: str, name: str):
    if "psycopg2.errors.UniqueViolation" in str(e):
        raise HTTPException(
            status_code=400,
            detail=f"{type} {name} already exists for given user and agent.",
        )

    raise HTTPException(status_code=500, detail=str(e))


def parse_task(t: SyncCeleryTaskMeta) -> AgentTaskResponse:
    result = None
    exception_snippet = None
    if t.status == "SUCCESS":
        result = pickle.loads(t.result)
    if t.status == "FAILURE":
        trace_lines = t.traceback.split("\n")
        if len(trace_lines) >= 2:
            # first 200 characters of the exception
            exception_snippet = trace_lines[-2][:200] + "...check logs for details"

    return AgentTaskResponse(
        task_id=t.task_id,
        status=t.status,
        name=t.name,
        retries=t.retries,
        result=result,
        exception_snippet=exception_snippet,
        date_done=str(t.date_done),
    )
