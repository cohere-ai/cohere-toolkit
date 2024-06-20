import logging
import os
from typing import Any, Dict, List

from compass_sdk import MetadataConfig, ParserConfig
from compass_sdk.compass import CompassClient
from compass_sdk.parser import CompassParserClient

from backend.tools.base import BaseTool

logger = logging.getLogger()


class CompassTool(BaseTool):
    """Tool to interact with a Compass instance."""

    @classmethod
    def is_available(cls) -> bool:
        vars = [
            "COHERE_COMPASS_URL",
            "COHERE_COMPASS_USERNAME",
            "COHERE_COMPASS_PASSWORD",
        ]
        return all(os.getenv(var) is not None for var in vars)

    def __init__(
        self,
        compass_url=None,
        compass_username=None,
        compass_password=None,
        metadata_config=MetadataConfig(),
        parser_config=ParserConfig(),
    ):
        """Initialize the Compass tool. Pass the Compass URL, username, and password
        as arguments or as environment variables."""
        self.url = compass_url or os.getenv("COHERE_COMPASS_URL")
        self.username = compass_username or os.getenv("COHERE_COMPASS_USERNAME")
        self.password = compass_password or os.getenv("COHERE_COMPASS_PASSWORD")
        self.parser_config = parser_config
        self.metadata_config = metadata_config
        try:
            # Try initializing Compass Parser and Client and call list_indexes
            # to check if the credentials are correct.
            self.parser_client = CompassParserClient(
                parser_url=self.url + "/parse",
                username=self.username,
                password=self.password,
                parser_config=self.parser_config,
                metadata_config=self.metadata_config,
            )
            self.compass_client = CompassClient(
                index_url=self.url,
                username=self.username,
                password=self.password,
            )
            self.compass_client.list_indexes()
        except Exception as e:
            logger.exception(f"Compass Tool: Error initializing Compass client: {e}")
            raise e

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        """Call the Compass tool. Allowed `action` values:
        - list_indexes: List all indexes in Compass.
        - create_index: Create a new index in Compass.
        - delete_index: Delete an existing index in Compass.
        - create: Create a new document in Compass.
        - search: Search for documents in Compass.
        - update: Update an existing document in Compass.
        - delete: Delete an existing document in Compass.
        """
        # Check if action is specified
        if not parameters.get("action", None):
            logger.error(
                "Compass Tool: No action specified. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )
            return
        # Check if action is valid
        valid_actions = [
            "list_indexes",
            "create_index",
            "delete_index",
            "create",
            "search",
            "update",
            "delete",
        ]
        if parameters["action"] not in valid_actions:
            logger.error(
                f"Compass Tool: Invalid action {parameters['action']}. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )
            return
        # Check if index is specified
        if not parameters.get("index", None) and parameters["action"] != "list_indexes":
            logger.error(
                "Compass Tool: No index specified. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )
            return
        # Index-related actions
        if parameters["action"] == "list_indexes":
            return self.compass_client.list_indexes()
        elif parameters["action"] == "create_index":
            return self.compass_client.create_index(index_name=parameters["index"])
        elif parameters["action"] == "delete_index":
            return self.compass_client.delete_index(index_name=parameters["index"])
        # Check if file_id is specified for file-related actions
        if not parameters.get("file_id", None):
            logger.error(
                "Compass Tool: No uninque identifier file_id specified. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )
            return
        # Create index if it does not exist
        self.compass_client.create_index(index_name=parameters.get("index"))
        # Perform the file-related action
        if parameters["action"] == "create":
            self._create(parameters, **kwargs)
        elif parameters["action"] == "search":
            self._search(parameters, **kwargs)
        elif parameters["action"] == "update":
            self._update(parameters, **kwargs)
        elif parameters["action"] == "delete":
            self._delete(parameters, **kwargs)

    def _parse(self, parameters: dict, **kwargs: Any) -> None:
        """Parse the input file."""
        if "file_path" not in parameters:
            logger.error(
                "Compass Tool: No file_path specified for "
                "create/update operation. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )
            return None
        file_path = parameters["file_path"]
        if not os.path.exists(file_path):
            logger.error(
                f"Compass Tool: File {file_path} does not exist. "
                "No action will be taken."
                f"Parameters specified: {parameters}"
            )
            return None
        parser_config = self.parser_config or parameters.get("parser_config", None)
        metadata_config = self.metadata_config or parameters.get(
            "metadata_config", None
        )
        return self.parser_client.process_file(
            file_path=file_path,
            file_id=parameters["file_id"],
            parser_config=parser_config,
            metadata_config=metadata_config,
            custom_context=parameters.get("custom_context", None),
            is_dataset=False,
        )

    def _create(self, parameters: dict, **kwargs: Any) -> Dict[str, str]:
        """Insert the document into Compass"""
        compass_docs = self._parse(parameters, **kwargs)
        if compass_docs is None:
            # Parsing failed
            return
        error = self.compass_client.insert_docs(
            index_name=parameters["index"], docs=compass_docs
        )
        if error is not None:
            logger.error(
                f"Compass Tool: Error inserting/updating document "
                f"into Compass: {error}"
            )

    def _search(self, parameters: dict, **kwargs: Any) -> None:
        """Run a search query on Compass and return the
        top_k results. By default, k=10."""
        if not parameters.get("query", None):
            logger.error(
                "Compass Tool: No search query specified. ",
                "Returning empty list. " "Parameters specified: {parameters}",
            )
            return []
        return self.compass_client.search(
            index_name=parameters["index"],
            query=parameters["query"],
            top_k=parameters.get("top_k", 10),
            filters=parameters.get("filters", None),
        )

    def _update(self, parameters: dict, **kwargs: Any) -> None:
        """Update file in Compass"""
        self._delete(parameters, **kwargs)
        self._create(parameters, **kwargs)

    def _delete(self, parameters: dict, **kwargs: Any) -> None:
        """Delete file from Compass"""
        self.compass_client.delete_document(
            index_name=parameters["index"], doc_id=parameters["file_id"]
        )
