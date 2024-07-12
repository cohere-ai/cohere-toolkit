import json
import logging
import os
from enum import Enum
from typing import Any, Dict, List

from backend.compass_sdk import (
    CompassDocument,
    MetadataConfig,
    ParserConfig,
    ProcessFileParameters,
)
from backend.compass_sdk.compass import CompassClient
from backend.compass_sdk.constants import DEFAULT_MAX_ACCEPTED_FILE_SIZE_BYTES
from backend.compass_sdk.parser import CompassParserClient

logger = logging.getLogger()


class Compass:
    """Interface to interact with a Compass instance."""

    class ValidActions(Enum):
        LIST_INDEXES = "list_indexes"
        CREATE_INDEX = "create_index"
        DELETE_INDEX = "delete_index"
        CREATE = "create"
        SEARCH = "search"
        UPDATE = "update"
        DELETE = "delete"
        GET_DOCUMENT = "get_document"
        ADD_CONTEXT = "add_context"
        REFRESH = "refresh"
        PROCESS_FILE = "process_file"

    def __init__(
        self,
        compass_api_url=None,
        compass_parser_url=None,
        compass_username=None,
        compass_password=None,
        metadata_config=MetadataConfig(),
        parser_config=ParserConfig(),
    ):
        """Initialize the Compass tool. Pass the Compass URL, username, and password
        as arguments or as environment variables."""
        vars = [
            "COHERE_COMPASS_API_URL",
            "COHERE_COMPASS_PARSER_URL",
            "COHERE_COMPASS_USERNAME",
            "COHERE_COMPASS_PASSWORD",
        ]
        if not all(os.getenv(var) is not None for var in vars):
            raise Exception(
                "Compass cannot be configured. Environment variables missing.",
            )

        self.compass_api_url = compass_api_url or os.getenv("COHERE_COMPASS_API_URL")
        self.compass_parser_url = compass_parser_url or os.getenv(
            "COHERE_COMPASS_PARSER_URL"
        )
        self.username = compass_username or os.getenv("COHERE_COMPASS_USERNAME")
        self.password = compass_password or os.getenv("COHERE_COMPASS_PASSWORD")
        self.parser_config = parser_config
        self.metadata_config = metadata_config
        try:
            # Try initializing Compass Parser and Client and call list_indexes
            # to check if the credentials are correct.
            self.parser_client = CompassParserClient(
                parser_url=self.compass_parser_url,
                username=self.username,
                password=self.password,
                parser_config=self.parser_config,
                metadata_config=self.metadata_config,
            )
            self.compass_client = CompassClient(
                index_url=self.compass_api_url,
                username=self.username,
                password=self.password,
            )
            self.compass_client.list_indexes()
        except Exception as e:
            logger.exception(f"Compass Tool: Error initializing Compass client: {e}")
            raise e

    def invoke(
        self,
        action: ValidActions,
        parameters: dict = {},
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Call the Compass tool. Allowed `action` values:
        - list_indexes: List all indexes in Compass.
        - create_index: Create a new index in Compass.
        - delete_index: Delete an existing index in Compass.
        - create: Create a new document in Compass.
        - search: Search for documents in Compass.
        - update: Update an existing document in Compass.
        - delete: Delete an existing document in Compass.
        """

        # Check if index is specified
        if not parameters.get("index", None) and action.value not in [
            self.ValidActions.LIST_INDEXES.value,
            self.ValidActions.PROCESS_FILE.value,
        ]:
            raise Exception(
                "Compass Tool: No index specified. ",
                "No action will be taken. ",
                f"Parameters specified: {parameters}",
            )

        # Index-related actions
        try:
            match action.value:
                case self.ValidActions.LIST_INDEXES.value:
                    return self.compass_client.list_indexes()
                case self.ValidActions.CREATE_INDEX.value:
                    return self.compass_client.create_index(
                        index_name=parameters["index"]
                    )
                case self.ValidActions.CREATE_INDEX.value:
                    return self.compass_client.delete_index(
                        index_name=parameters["index"]
                    )
                case self.ValidActions.CREATE.value:
                    self._create(parameters, **kwargs)
                case self.ValidActions.SEARCH.value:
                    return self._search(parameters, **kwargs)
                case self.ValidActions.UPDATE.value:
                    self._update(parameters, **kwargs)
                case self.ValidActions.DELETE.value:
                    self._delete(parameters, **kwargs)
                case self.ValidActions.GET_DOCUMENT.value:
                    return self._get_document(parameters, **kwargs)
                case self.ValidActions.ADD_CONTEXT.value:
                    self._add_context(parameters, **kwargs)
                case self.ValidActions.REFRESH.value:
                    self._refresh(parameters, **kwargs)
                case self.ValidActions.PROCESS_FILE.value:
                    return self._process_file(parameters, **kwargs)
                case _:
                    raise Exception(
                        f"Compass Tool: Invalid action {parameters['action']}. "
                        "No action will be taken. "
                        f"Parameters specified: {parameters}"
                    )
        except Exception as e:
            message = "Compass Error: {}".format(str(e))
            logger.error(message)
            raise Exception(message)

    def _create(self, parameters: dict, **kwargs: Any) -> Dict[str, str]:
        """Insert the document into Compass"""
        compass_docs = self._process_file(parameters, **kwargs)
        if compass_docs is None:
            raise Exception("Parsing failed")

        if doc_metadata := parameters.get("metadata", None):
            for doc in compass_docs:
                doc.metadata.meta.append(doc_metadata)

        error = self.compass_client.insert_docs(
            index_name=parameters["index"],
            docs=compass_docs,
        )
        if error is not None:
            message = ("Compass Tool: Error inserting/updating document ",)
            f"into Compass: {error}"
            raise Exception(message)

    def _search(self, parameters: dict, **kwargs: Any) -> None:
        """Run a search query on Compass and return the
        top_k results. By default, k=10."""
        if not parameters.get("query", None):
            message = ("Compass Tool: No search query specified. ",)
            ("Returning empty list. " "Parameters specified: {parameters}",)
            raise Exception(message)

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
        # Check if file_id is specified for file-related actions
        if not parameters.get("file_id", None):
            raise Exception(
                "Compass Tool: No uninque identifier file_id specified. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )
        self.compass_client.delete_document(
            index_name=parameters["index"],
            doc_id=parameters["file_id"],
        )

    def _get_document(self, parameters: dict, **kwargs: Any) -> None:
        """Get document with id from Compass"""
        # Check if file_id is specified for file-related actions
        if not parameters.get("file_id", None):
            raise Exception(
                "Compass Tool: No uninque identifier file_id specified. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )
        return self.compass_client.get_document(
            index_name=parameters["index"],
            doc_id=parameters["file_id"],
        )

    def _add_context(self, parameters: dict, **kwargs: Any) -> None:
        """Adds context to a document with id in Compass"""
        # Check if file_id is specified for file-related actions
        if not parameters.get("file_id", None):
            raise Exception(
                "Compass Tool: No uninque identifier file_id specified. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )
        if not parameters.get("context", None):
            raise Exception(
                "Compass Tool: Context cannot be empty. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )
        self.compass_client.add_context(
            index_name=parameters["index"],
            doc_id=parameters["file_id"],
            context=parameters["context"],
        )

    def _refresh(self, parameters: dict, **kwargs: Any) -> None:
        """Refresh an index in Compass"""
        self.compass_client.refresh(index_name=parameters["index"])

    def _process_file(self, parameters: dict, **kwargs: Any) -> None:
        """Parse the input file."""
        # Check if file_id is specified for file-related actions
        if not parameters.get("file_id", None):
            raise Exception(
                "Compass Tool: No uninque identifier file_id specified. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )

        # Check if filename is specified for file-related actions
        if not parameters.get("filename", None) and not parameters.get(
            "file_text", None
        ):
            logger.error(
                "Compass Tool: No filename or file_text specified for "
                "create/update operation. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )
            return None

        file_id = parameters["file_id"]
        filename = parameters.get("filename", None)
        file_text = parameters.get("file_text", None)

        if filename and not os.path.exists(filename):
            logger.error(
                f"Compass Tool: File {filename} does not exist. "
                "No action will be taken."
                f"Parameters specified: {parameters}"
            )
            return None

        parser_config = self.parser_config or parameters.get("parser_config", None)
        metadata_config = metadata_config = self.metadata_config or parameters.get(
            "metadata_config", None
        )

        if filename:
            return self.parser_client.process_file(
                filename=filename,
                file_id=file_id,
                parser_config=parser_config,
                metadata_config=metadata_config,
                is_dataset=False,
                custom_context=parameters.get("custom_context", None),
            )
        else:
            return self._raw_parsing(
                text=file_text,
                file_id=file_id,
                bytes_content=isinstance(file_text, bytes),
            )

    def _raw_parsing(self, text: str, file_id: str, bytes_content: bool):
        text_bytes = str.encode(text) if not bytes_content else text
        if len(text_bytes) > DEFAULT_MAX_ACCEPTED_FILE_SIZE_BYTES:
            logger.error(
                f"File too large, supported file size is {DEFAULT_MAX_ACCEPTED_FILE_SIZE_BYTES / 1000_1000} "
                f"mb, file_id {file_id}"
            )
            return []

        params = ProcessFileParameters(
            parser_config=self.parser_config,
            metadata_config=self.metadata_config,
            doc_id=file_id,
        )
        auth = (
            (self.username, self.password) if self.username and self.password else None
        )
        res = self.parser_client.session.post(
            url=f"{self.parser_client.parser_url}/v1/process_file",
            data={"data": json.dumps(params.model_dump())},
            files={"file": (file_id, text_bytes)},
            auth=auth,
        )

        if res.ok:
            docs = [CompassDocument(**doc) for doc in res.json()["docs"]]
            for doc in docs:
                additional_metadata = CompassParserClient._get_metadata(doc=doc)
                doc.content = {**doc.content, **additional_metadata}
        else:
            docs = []
            logger.error(f"Error processing file: {res.text}")

        return docs
