import asyncio
from typing import Any, Dict, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.chat.collate import rerank_and_chunk, to_dict
from backend.config.tools import get_available_tools
from backend.model_deployments.base import BaseDeployment
from backend.schemas.context import Context
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import (
    ToolAuthException,
    ToolErrorCode,
)

TIMEOUT_SECONDS = 60

logger = LoggerFactory().get_logger()


async def async_call_tools(
    chat_history: List[Dict[str, Any]],
    deployment_model: BaseDeployment,
    ctx: Context,
    **kwargs: Any,
) -> list[dict[str, str]]:
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

    tool_results = await _call_all_tools_async(
        kwargs.get("session"), tool_calls, deployment_model, ctx
    )

    tool_results = await rerank_and_chunk(tool_results, deployment_model, ctx, **kwargs)
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
    combined = asyncio.gather(*tasks)
    try:
        tool_results = await asyncio.wait_for(combined, timeout=TIMEOUT_SECONDS)
        # Flatten a list of list of tool results
        return [n for m in tool_results for n in m]
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=500,
            detail=f"Timeout while calling tools with timeout: {TIMEOUT_SECONDS}",
        )



async def _call_tool_async(
    ctx: Context,
    db: Session,
    tool_call: dict,
    deployment_model: BaseDeployment,
) -> List[Dict[str, Any]]:
    tool_definition = get_available_tools().get(tool_call["name"])
    if not tool_definition:
        logger.info(
            event=f"[Custom Chat] Tool not included in tools parameter: {tool_call['name']}",
        )
        outputs = [
            {
                "call": tool_call,
                "outputs": [{"text": f"Tool {tool_call['name']} not found", "success": False}],
            }
        ]
        return outputs

    tool = tool_definition.implementation()

    try:
        outputs = await tool.call(
            parameters=tool_call.get("parameters"),
            ctx=ctx,
            session=db,
            model_deployment=deployment_model,
            user_id=ctx.get_user_id(),
            trace_id=ctx.get_trace_id(),
            agent_id=ctx.get_agent_id(),
            conversation_id=ctx.get_conversation_id(),
            agent_tool_metadata=ctx.get_agent_tool_metadata(),
        )
    except ToolAuthException as e:
        return [
            {
                "call": tool_call,
                "outputs": tool.get_tool_error(
                    details=str(e),
                    text="Tool authentication failed",
                    error_type=ToolErrorCode.AUTH,
                ),
            }
        ]
    except Exception as e:
        return [
            {
                "call": tool_call,
                "outputs": tool.get_tool_error(details=str(e)),
            }
        ]

    # If the tool returns a list of outputs, append each output to the tool_results list
    # Otherwise, append the single output to the tool_results list
    outputs = outputs if isinstance(outputs, list) else [outputs]
    return [{"call": tool_call, "outputs": outputs}]
