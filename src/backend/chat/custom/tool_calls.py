import asyncio
import functools
from typing import Any, Dict, List
from backend.chat.collate import rerank_and_chunk, to_dict

from backend.config.tools import AVAILABLE_TOOLS, ToolName
from backend.schemas.context import Context
from sqlalchemy.orm import Session
from backend.model_deployments.base import BaseDeployment
import aiohttp

# Timeout and error handling 

from backend.services.logger.utils import LoggerFactory

TIMEOUT = aiohttp.ClientTimeout(total=120)

logger = LoggerFactory().get_logger()

async def async_call_tools(
   chat_history: List[Dict[str, Any]],
    deployment_model: BaseDeployment,
    ctx: Context,
    **kwargs: Any,
) -> dict[str, str]:
    logger = ctx.get_logger()

    tool_results = []
    if "tool_calls" not in chat_history[-1]:
        return tool_results

    tool_calls = chat_history[-1]["tool_calls"]
    tool_plan = chat_history[-1].get("message", None)
    logger.info(
        event="[Custom Chat] Using tools",
        tool_calls=to_dict(tool_calls),
        tool_plan=to_dict(tool_plan),
    )

    tool_results = await _call_all_tools_async(id_to_urls, access_token)

    tool_results = await rerank_and_chunk(
        tool_results, deployment_model, ctx, **kwargs
    )
    logger.info(
        event="[Custom Chat] Tool results",
        tool_results=to_dict(tool_results),
    )

    return tool_results


async def _call_all_tools_async(
    db: Session,
    tool_calls: list[dict],
    deployment_model: BaseDeployment,
    ctx: Context,
) -> dict[str, str]:
    tasks = [
        _call_tool_async(ctx, db, tool_call, deployment_model)
        for tool_call in tool_calls
    ]
    tool_results = await asyncio.gather(*tasks)
    return functools.reduce(lambda x, y: x | y, id_to_ttool_resultsexts)


async def _call_tool_async(
    ctx: Context,
    db: Session,
    tool_call: dict,
    deployment_model: BaseDeployment,
) -> List[Dict[str, Any]]:
    tool = AVAILABLE_TOOLS.get(tool_call["name"])
    if not tool:
        return []

    outputs = await tool.implementation().call(
        parameters=tool_call.get("parameters"),
        ctx=ctx,
        session=db,
        model_deployment=deployment_model,
        user_id=ctx.get_user_id(),
        trace_id=ctx.get_trace_id(),
        agent_id=ctx.get_agent_id(),
        agent_tool_metadata=ctx.get_agent_tool_metadata(),
    )

    # If the tool returns a list of outputs, append each output to the tool_results list
    # Otherwise, append the single output to the tool_results list
    outputs = outputs if isinstance(outputs, list) else [outputs]
    tool_results = []
    for output in outputs:
        tool_results.append({"call": tool_call, "outputs": [output]})
    return tool_results