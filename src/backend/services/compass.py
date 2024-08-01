import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional

from backend.compass_sdk import (
    CompassDocument,
    MetadataConfig,
    ParserConfig,
    ProcessFileParameters,
)
from backend.compass_sdk.compass import CompassClient
from backend.compass_sdk.constants import DEFAULT_MAX_ACCEPTED_FILE_SIZE_BYTES
from backend.compass_sdk.parser import CompassParserClient
from backend.config.settings import Settings
from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()


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
        compass_api_url: Optional[str] = None,
        compass_parser_url: Optional[str] = None,
        compass_username: Optional[str] = None,
        compass_password: Optional[str] = None,
        metadata_config=MetadataConfig(),
        parser_config=ParserConfig(),
    ):
        """Initialize the Compass tool. Pass the Compass URL, username, and password
        as arguments or as environment variables."""
        self.compass_api_url = compass_api_url or Settings().tools.compass.api_url
        self.compass_parser_url = (
            compass_parser_url or Settings().tools.compass.parser_url
        )
        self.username = compass_username or Settings().tools.compass.username
        self.password = compass_password or Settings().tools.compass.password
        if self.compass_api_url is None or self.compass_parser_url is None:
            message = "[Compass] Error initializing Compass client: API url or parser url missing."
            logger.exception(event=message)
            raise Exception(message)
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
            logger.exception(event=f"[Compass] Error initializing Compass client: {e}")
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
                f"[Compass] Error invoking Compass: No index specified in parameters {parameters}",
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
                        f"[Compass] Error invoking Compass: Invalid action in parameters {parameters}"
                    )
        except Exception as e:
            message = f"[Compass] Error invoking Compass: {e}"
            logger.error(event=message)
            raise Exception(message)

    def _create(self, parameters: dict, **kwargs: Any) -> Dict[str, str]:
        """Insert the document into Compass"""
        compass_docs = self._process_file(parameters, **kwargs)
        if compass_docs is None:
            raise Exception(
                "[Compass] Error inserting document: Failed to process file"
            )

        if doc_metadata := parameters.get("metadata", None):
            for doc in compass_docs:
                doc.metadata.meta.append(doc_metadata)

        error = self.compass_client.insert_docs(
            index_name=parameters["index"],
            docs=compass_docs,
        )
        if error is not None:
            message = ("[Compass] Error inserting document: {error}",)
            logger.error(event=message)
            raise Exception(message)

    def _search(self, parameters: dict, **kwargs: Any) -> None:
        """Run a search query on Compass and return the
        top_k results. By default, k=10."""
        if not parameters.get("query", None):
            message = f"[Compass] Error searching Compass: No search query specified in parameters {parameters}"
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
                f"[Compass] Error deleting file: No file_id in parameters {parameters}"
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
                f"[Compass] Error fetching document: No file_id in parameters {parameters}"
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
                f"[Compass] Error adding context: No file_id in parameters {parameters}"
            )
        if not parameters.get("context", None):
            raise Exception(
                f"[Compass] Error adding context: Context cannot be empty for parameters {parameters}"
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
                f"[Compass] Error processing file: No file_id specified in parameters {parameters}"
            )

        # Check if filename is specified for file-related actions
        if not parameters.get("filename", None) and not parameters.get(
            "file_text", None
        ):
            logger.error(
                event=f"[Compass] Error processing file: No filename or file_text specified in parameters {parameters}"
            )
            return None

        file_id = parameters["file_id"]
        filename = parameters.get("filename", None)
        file_text = parameters.get("file_text", None)

        if filename and not os.path.exists(filename):
            logger.error(
                event=f"[Compass] Error processing file: Invalid filename {filename} in parameters {parameters}"
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
                event=f"[Compass] Error parsing file: File Size is too large {len(text_bytes)}",
                max_size=DEFAULT_MAX_ACCEPTED_FILE_SIZE_BYTES,
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
            logger.error(event=f"[Compass] Error processing file: {res.text}")

        return docs
