"""
Query and Path Parameters for Agents
"""
from fastapi import Path

agent_id_path = Path(
    title="Agent ID",
    description="Agent ID for agent in question",
)

agent_tool_metadata_id_path = Path(
    title="Agent Tool Metadata ID",
    description="Agent Tool Metadata ID for tool metadata in question",
)

file_id_path = Path(
    title="File ID",
    description="File ID for file in question",
)
