import os
import threading
from collections import deque
from dataclasses import dataclass
from statistics import mean
from typing import Dict, Iterator, List, Optional, Tuple, Union

import requests
from joblib import Parallel, delayed
from pydantic import BaseModel
from requests.exceptions import InvalidSchema
from tenacity import (
    RetryError,
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_fixed,
)
from tqdm import tqdm

from backend.compass_sdk import (
    BatchPutDocumentsInput,
    Chunk,
    CompassDocument,
    CompassDocumentStatus,
    CompassSdkStage,
    Document,
    LoggerLevel,
    PutDocumentsInput,
    SearchFilter,
    SearchInput,
    logger,
)
from backend.compass_sdk.constants import (
    DEFAULT_MAX_CHUNKS_PER_REQUEST,
    DEFAULT_MAX_ERROR_RATE,
    DEFAULT_MAX_RETRIES,
    DEFAULT_SLEEP_RETRY_SECONDS,
)


@dataclass
class RetryResult:
    result: Optional[dict] = None
    error: Optional[str] = None


class CompassAuthError(Exception):
    """Exception raised for authentication errors in the Compass client."""

    def __init__(
        self,
        message=(
            "Unauthorized. Please check your username and password, "
            "which can be passed into CompassClient or set with "
            "COHERE_COMPASS_USERNAME and COHERE_COMPASS_PASSWORD "
            "environment variables."
        ),
    ):
        self.message = message
        super().__init__(self.message)


class CompassMaxErrorRateExceeded(Exception):
    """Exception raised when the error rate exceeds the maximum allowed error rate in the Compass client."""

    def __init__(
        self,
        message="The maximum error rate was exceeded. Stopping the insertion process.",
    ):
        self.message = message
        super().__init__(self.message)


class CompassClient:
    def __init__(
        self,
        index_url: str = "http://localhost:80",
        username: Optional[str] = None,
        password: Optional[str] = None,
        logger_level: LoggerLevel = LoggerLevel.INFO,
    ):
        """
        A compass client to interact with the Compass API
        :param index_url: the url of the Compass instance
        :param username: the username for the Compass instance
        :param password: the password for the Compass instance
        """
        self.index_url = index_url
        self.username = username or os.getenv("COHERE_COMPASS_USERNAME")
        self.password = password or os.getenv("COHERE_COMPASS_PASSWORD")
        self.session = requests.Session()

        self.function_call = {
            "create_index": self.session.put,
            "list_indexes": self.session.get,
            "delete_index": self.session.delete,
            "delete_document": self.session.delete,
            "get_document": self.session.get,
            "put_documents": self.session.put,
            "put_documents_batch": self.session.post,
            "search_documents": self.session.post,
            "add_context": self.session.post,
            "refresh": self.session.post,
        }
        self.function_endpoint = {
            "create_index": "/api/v1/indexes/{index_name}",
            "list_indexes": "/api/v1/indexes",
            "delete_index": "/api/v1/indexes/{index_name}",
            "delete_document": "/api/v1/indexes/{index_name}/documents/{doc_id}",
            "get_document": "/api/v1/indexes/{index_name}/documents/{doc_id}",
            "put_documents": "/api/v1/indexes/{index_name}/documents",
            "put_documents_batch": "/api/v1/batch/indexes/{index_name}",
            "search_documents": "/api/v1/indexes/{index_name}/documents/search",
            "add_context": "/api/v1/indexes/{index_name}/documents/add_context/{doc_id}",
            "refresh": "/api/v1/indexes/{index_name}/refresh",
        }
        logger.setLevel(logger_level.value)

    def create_index(self, index_name: str):
        """
        Create an index in Compass
        :param index_name: the name of the index
        :return: the response from the Compass API
        """
        return self._send_request(
            function="create_index",
            index_name=index_name,
            max_retries=DEFAULT_MAX_RETRIES,
            sleep_retry_seconds=DEFAULT_SLEEP_RETRY_SECONDS,
        )

    def refresh(self, index_name: str):
        """
        Refresh index
        :param index_name: the name of the index
        :return: the response from the Compass API
        """
        return self._send_request(
            function="refresh",
            index_name=index_name,
            max_retries=DEFAULT_MAX_RETRIES,
            sleep_retry_seconds=DEFAULT_SLEEP_RETRY_SECONDS,
        )

    def delete_index(self, index_name: str):
        """
        Delete an index from Compass
        :param index_name: the name of the index
        :return: the response from the Compass API
        """
        return self._send_request(
            function="delete_index",
            index_name=index_name,
            max_retries=DEFAULT_MAX_RETRIES,
            sleep_retry_seconds=DEFAULT_SLEEP_RETRY_SECONDS,
        )

    def delete_document(self, index_name: str, doc_id: str):
        """
        Delete a document from Compass
        :param index_name: the name of the index
        :doc_id: the id of the document
        :return: the response from the Compass API
        """
        return self._send_request(
            function="delete_document",
            index_name=index_name,
            doc_id=doc_id,
            max_retries=DEFAULT_MAX_RETRIES,
            sleep_retry_seconds=DEFAULT_SLEEP_RETRY_SECONDS,
        )

    def get_document(self, index_name: str, doc_id: str):
        """
        Get a document from Compass
        :param index_name: the name of the index
        :doc_id: the id of the document
        :return: the response from the Compass API
        """
        return self._send_request(
            function="get_document",
            index_name=index_name,
            doc_id=doc_id,
            max_retries=DEFAULT_MAX_RETRIES,
            sleep_retry_seconds=DEFAULT_SLEEP_RETRY_SECONDS,
        )

    def list_indexes(self):
        """
        List all indexes in Compass
        :return: the response from the Compass API
        """
        return self._send_request(
            function="list_indexes",
            index_name="",
            max_retries=DEFAULT_MAX_RETRIES,
            sleep_retry_seconds=DEFAULT_SLEEP_RETRY_SECONDS,
        )

    def add_context(
        self,
        index_name: str,
        doc_id: str,
        context: Dict,
        max_retries: int = DEFAULT_MAX_RETRIES,
        sleep_retry_seconds: int = DEFAULT_SLEEP_RETRY_SECONDS,
    ) -> Optional[RetryResult]:
        """
        Update the content field of an existing document with additional context

        :param index_name: the name of the index
        :param doc_id: the document to modify
        :param context: A dictionary of key:value pairs to insert into the content field of a document
        :param max_retries: the maximum number of times to retry a doc insertion
        :param sleep_retry_seconds: number of seconds to go to sleep before retrying a doc insertion
        """

        return self._send_request(
            function="add_context",
            index_name=index_name,
            doc_id=doc_id,
            data=context,
            max_retries=max_retries,
            sleep_retry_seconds=sleep_retry_seconds,
        )

    def insert_doc(
        self,
        index_name: str,
        doc: CompassDocument,
        max_retries: int = DEFAULT_MAX_RETRIES,
        sleep_retry_seconds: int = DEFAULT_SLEEP_RETRY_SECONDS,
    ) -> Optional[List[CompassDocument]]:
        """
        Insert a parsed document into an index in Compass
        :param index_name: the name of the index
        :param doc: the parsed compass document
        :param max_retries: the maximum number of times to retry a doc insertion
        :param sleep_retry_seconds: number of seconds to go to sleep before retrying a doc insertion
        """
        return self.insert_docs(
            index_name=index_name,
            docs=iter([doc]),
            max_retries=max_retries,
            sleep_retry_seconds=sleep_retry_seconds,
        )

    def insert_docs_batch(self, uuid: str, index_name: str):
        """
        Insert a batch of parsed documents into an index in Compass
        :param uuid: the uuid of the batch
        :param index_name: the name of the index
        """
        return self._send_request(
            function="put_documents_batch",
            index_name=index_name,
            data=BatchPutDocumentsInput(uuid=uuid),
            max_retries=DEFAULT_MAX_RETRIES,
            sleep_retry_seconds=DEFAULT_SLEEP_RETRY_SECONDS,
        )

    def batch_status(self, uuid: str):
        """
        Get the status of a batch
        :param uuid: the uuid of the batch
        """
        auth = (
            (self.username, self.password) if self.username and self.password else None
        )
        resp = self.session.get(
            url=f"{self.index_url}/api/v1/batch/status/{uuid}",
            auth=auth,
        )

        if resp.ok:
            return resp.json()
        else:
            raise Exception(
                f"Failed to get batch status: {resp.status_code} {resp.text}"
            )

    def insert_docs(
        self,
        index_name: str,
        docs: Iterator[CompassDocument],
        max_chunks_per_request: int = DEFAULT_MAX_CHUNKS_PER_REQUEST,
        max_error_rate: float = DEFAULT_MAX_ERROR_RATE,
        max_retries: int = DEFAULT_MAX_RETRIES,
        sleep_retry_seconds: int = DEFAULT_SLEEP_RETRY_SECONDS,
        errors_sliding_window_size: Optional[int] = 10,
        skip_first_n_docs: int = 0,
        num_jobs: Optional[int] = None,
    ) -> Optional[List[CompassDocument]]:
        """
        Insert multiple parsed documents into an index in Compass
        :param index_name: the name of the index
        :param docs: the parsed documents
        :param max_chunks_per_request: the maximum number of chunks to send in a single API request
        :param num_jobs: the number of parallel jobs to use
        :param max_error_rate: the maximum error rate allowed
        :param max_retries: the maximum number of times to retry a request if it fails
        :param sleep_retry_seconds: the number of seconds to wait before retrying an API request
        :param errors_sliding_window_size: the size of the sliding window to keep track of errors
        :param skip_first_n_docs: number of docs to skip indexing. Useful when insertion failed after N documents
        """

        def put_request(
            request_data: List[Tuple[CompassDocument, Document]],
            previous_errors: List[CompassDocument],
            num_doc: int,
        ) -> None:
            nonlocal num_succeeded, errors
            errors.extend(previous_errors)
            compass_docs: List[CompassDocument] = [
                compass_doc for compass_doc, _ in request_data
            ]
            put_docs_input = PutDocumentsInput(
                docs=[input_doc for _, input_doc in request_data]
            )

            # It could be that all documents have errors, in which case we should not send a request
            # to the Compass Server. This is a common case when the parsing of the documents fails.
            # In this case, only errors will appear in the insertion_docs response
            if not request_data:
                return

            results = self._send_request(
                function="put_documents",
                index_name=index_name,
                data=put_docs_input,
                max_retries=max_retries,
                sleep_retry_seconds=sleep_retry_seconds,
            )

            if results.error:
                for doc in compass_docs:
                    doc.errors.append({CompassSdkStage.Indexing: results.error})
                    errors.append(doc)
            else:
                num_succeeded += len(compass_docs)

            # Keep track of the results of the last N API calls to calculate the error rate
            # If the error rate is higher than the threshold, stop the insertion process
            error_window.append(results.error)
            error_rate = (
                mean([1 if x else 0 for x in error_window])
                if len(error_window) == error_window.maxlen
                else 0
            )
            if error_rate > max_error_rate:
                raise CompassMaxErrorRateExceeded(
                    f"[Thread {threading.get_native_id()}]{error_rate * 100}% of insertions failed "
                    f"in the last {errors_sliding_window_size} API calls. Stopping the insertion process."
                )

        error_window = deque(
            maxlen=errors_sliding_window_size
        )  # Keep track of the results of the last N API calls
        num_succeeded = 0
        errors = []
        requests_iter = tqdm(self._get_request_blocks(docs, max_chunks_per_request))

        try:
            num_jobs = num_jobs or os.cpu_count()
            Parallel(n_jobs=num_jobs, backend="threading")(
                delayed(put_request)(
                    request_data=request_block,
                    previous_errors=previous_errors,
                    num_doc=i,
                )
                for i, (request_block, previous_errors) in enumerate(requests_iter, 1)
                if i > skip_first_n_docs
            )
        except CompassMaxErrorRateExceeded as e:
            logger.error(e.message)
        return errors if len(errors) > 0 else None

    @staticmethod
    def _get_request_blocks(
        docs: Iterator[CompassDocument],
        max_chunks_per_request: int,
    ) -> Iterator:
        """
        Create request blocks to send to the Compass API
        :param docs: the documents to send
        :param max_chunks_per_request: the maximum number of chunks to send in a single API request
        :return: an iterator over the request blocks
        """

        request_block, errors = [], []
        num_chunks = 0
        for num_doc, doc in enumerate(docs, 1):
            if doc.status != CompassDocumentStatus.Success:
                logger.error(
                    f"[Thread {threading.get_native_id()}] Document #{num_doc} has errors: {doc.errors}"
                )
                errors.append(doc)
            else:
                num_chunks += (
                    len(doc.chunks)
                    if doc.status == CompassDocumentStatus.Success
                    else 0
                )
                if num_chunks > max_chunks_per_request:
                    yield request_block, errors
                    request_block, errors = [], []
                    num_chunks = 0

                request_block.append(
                    (
                        doc,
                        Document(
                            doc_id=doc.metadata.doc_id,
                            path=doc.metadata.filename,
                            content=doc.content,
                            chunks=[Chunk(**c.model_dump()) for c in doc.chunks],
                            index_fields=doc.index_fields,
                        ),
                    )
                )

        if len(request_block) > 0 or len(errors) > 0:
            yield request_block, errors

    def search(
        self,
        index_name: str,
        query: str,
        top_k: int = 10,
        filters: Optional[List[SearchFilter]] = None,
    ):
        """
        Search your Compass index
        :param index_name: the name of the index
        :param query: query to search for
        :param top_k: number of documents to return
        """
        return self._send_request(
            function="search_documents",
            index_name=index_name,
            data=SearchInput(query=query, top_k=top_k, filters=filters),
            max_retries=1,
            sleep_retry_seconds=1,
        )

    def _send_request(
        self,
        index_name: str,
        function: str,
        max_retries: int,
        sleep_retry_seconds: int,
        data: Optional[Union[Dict, BaseModel]] = None,
        doc_id: Optional[str] = None,
    ) -> RetryResult:
        """
        Send a request to the Compass API
        :param function: the function to call
        :param index_name: the name of the index
        :param max_retries: the number of times to retry the request
        :param sleep_retry_seconds: the number of seconds to sleep between retries
        :param data: the data to send
        :return: An error message if the request failed, otherwise None
        """

        @retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_fixed(sleep_retry_seconds),
            retry=retry_if_not_exception_type((CompassAuthError, InvalidSchema)),
        )
        def _send_request_with_retry():
            nonlocal error
            try:
                if data:
                    if isinstance(data, BaseModel):
                        data_dict = data.model_dump()
                    elif isinstance(data, Dict):
                        data_dict = data

                    response = self.function_call[function](
                        target_path, json=data_dict, auth=(self.username, self.password)
                    )
                else:
                    response = self.function_call[function](
                        target_path, auth=(self.username, self.password)
                    )

                if response.ok:
                    error = None
                    return RetryResult(result=response.json(), error=None)
                else:
                    response.raise_for_status()

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    error = "Unauthorized. Please check your username and password."
                    raise CompassAuthError()
                else:
                    error = str(e) + " " + e.response.text
                    logger.error(
                        f"[Thread {threading.get_native_id()}] Failed to send request to "
                        f"{function} {target_path}: {type(e)} {error}. Going to sleep for "
                        f"{sleep_retry_seconds} seconds and retrying."
                    )
                    raise e

            except Exception as e:
                error = str(e)
                logger.error(
                    f"[Thread {threading.get_native_id()}] Failed to send request to "
                    f"{function} {target_path}: {type(e)} {error}. Going to sleep for "
                    f"{sleep_retry_seconds} seconds and retrying."
                )
                raise e

        error = None
        try:
            target_path = self.index_url + self.function_endpoint[function].format(
                index_name=index_name, doc_id=doc_id
            )
            res = _send_request_with_retry()
            if res:
                return res
            else:
                return RetryResult(result=None, error=error)
        except RetryError:
            logger.error(
                f"[Thread {threading.get_native_id()}] Failed to send request after {max_retries} attempts. Aborting."
            )
            return RetryResult(result=None, error=error)
