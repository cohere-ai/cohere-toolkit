import json
from typing import Any, Dict, List

from fastapi import Depends

from backend.model_deployments.base import BaseDeployment
from backend.schemas.context import Context
from backend.services.context import get_context

RELEVANCE_THRESHOLD = 0.1


async def rerank_and_chunk(
    tool_results: List[Dict[str, Any]],
    model: BaseDeployment,
    ctx: Context,
    **kwargs: Any
) -> List[Dict[str, Any]]:
    """
    Takes a list of tool_results and internally reranks the documents for each query, if there's one e.g:
    [{"q1":[1, 2, 3],"q2": [4, 5, 6]] -> [{"q1":[2 , 3, 1],"q2": [4, 6, 5]]

    Args:
        tool_results (List[Dict[str, Any]]): List of tool_results from different retrievers.
            Each tool_result contains a ToolCall and a list of Outputs.
        model (BaseDeployment): Model deployment.
        ctx (Context): Context object.
        kwargs (Any): Additional arguments.

    Returns:
        List[Dict[str, Any]]: List of reranked and combined documents.
    """
    # If rerank is not enabled return documents as is:
    if not model.rerank_enabled:
        return tool_results

    # Merge all the documents with the same tool call and parameters
    unified_tool_results = {}
    for tool_result in tool_results:
        tool_call = tool_result["call"]
        tool_call_hashable = str(tool_call)

        if tool_call_hashable not in unified_tool_results.keys():
            unified_tool_results[tool_call_hashable] = {
                "call": tool_call,
                "outputs": [],
            }

        unified_tool_results[tool_call_hashable]["outputs"].extend(
            tool_result["outputs"]
        )

    # Rerank the documents for each query
    reranked_results = {}
    for tool_call_hashable, tool_result in unified_tool_results.items():
        tool_call = tool_result["call"]
        query = tool_call.get("parameters").get("query") or tool_call.get(
            "parameters"
        ).get("search_query")

        # Only rerank if there is a query
        if not query:
            reranked_results[tool_call_hashable] = tool_result
            continue

        chunked_outputs = []
        for output in tool_result["outputs"]:
            text = output.get("text")

            if not text:
                chunked_outputs.append([output])
                continue

            chunks = chunk(text)
            chunked_outputs.extend([dict(output, text=chunk) for chunk in chunks])

        # If no documents to rerank, continue to the next query
        if not chunked_outputs:
            continue

        res = await model.invoke_rerank(
            query=query,
            documents=chunked_outputs,
            ctx=ctx,
        )

        if not res:
            reranked_results[tool_call_hashable] = tool_result
            continue

        # Sort the results by relevance score
        res["results"].sort(key=lambda x: x["relevance_score"], reverse=True)

        # Map the results back to the original documents
        reranked_results[tool_call_hashable] = {
            "call": tool_call,
            "outputs": [
                chunked_outputs[r["index"]]
                for r in res["results"]
                if r["relevance_score"] > RELEVANCE_THRESHOLD
            ],
        }

    return list(reranked_results.values())


def chunk(content, compact_mode=False, soft_word_cut_off=100, hard_word_cut_off=300):
    if compact_mode:
        content = content.replace("\n", " ")

    chunks = []
    current_chunk = ""
    words = content.split()
    word_count = 0

    for word in words:
        if word_count + len(word.split()) > hard_word_cut_off:
            # If adding the next word exceeds the hard limit, finalize the current chunk
            chunks.append(current_chunk)
            current_chunk = ""
            word_count = 0

        if word_count + len(word.split()) > soft_word_cut_off and word.endswith("."):
            # If adding the next word exceeds the soft limit and the word ends with a period, finalize the current chunk
            current_chunk += " " + word
            chunks.append(current_chunk.strip())
            current_chunk = ""
            word_count = 0
        else:
            # Add the word to the current chunk
            if current_chunk == "":
                current_chunk = word
            else:
                current_chunk += " " + word
            word_count += len(word.split())

    # Add any remaining content as the last chunk
    if current_chunk != "":
        chunks.append(current_chunk.strip())

    return chunks


def to_dict(obj):
    return json.loads(
        json.dumps(
            obj, default=lambda o: o.__dict__ if hasattr(o, "__dict__") else str(o)
        )
    )
