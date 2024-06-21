import datetime
import logging
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from backend.tools.base import BaseTool
from backend.tools.compass import CompassTool

logger = logging.getLogger()


# Scopes of the Drive API
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
]


# File types to export from Google Drive. Other file formats will not be exported
ALLOWED_FILE_TYPES = [
    "application/vnd.google-apps.document",  # Google Docs
    "application/vnd.google-apps.spreadsheet",  # Google Sheets
    "application/vnd.google-apps.presentation",  # Google Slides
    "application/pdf",  # PDF
    "text/csv",  # CSV
    "application/json",  # JSON
    "text/plain",  # TXT
]


# Export file formats
FILE_EXPORT_TYPES = {
    "application/vnd.google-apps.document": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "docx",
    ),
    "application/vnd.google-apps.spreadsheet": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xlsx",
    ),
    "application/vnd.google-apps.presentation": (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "pptx",
    ),
    "application/pdf": ("application/pdf", "pdf"),
    "text/csv": ("text/csv", "csv"),
    "application/json": ("application/json", "json"),
    "text/plain": ("text/plain", "txt"),
}

# Constants for search
DRIVE_SEARCH_MULTIPLE = 3
COMPASS_SEARCH_MULTIPLE = 3


class GoogleDrive(BaseTool):
    @classmethod
    def is_available(cls):
        return os.getenv("GOOGLE_CREDENTIALS")

    def __init__(self):
        """Initialize a google drive tool"""
        self.user_id = os.getenv("GOOGLE_USER_ID")
        self.credentials = os.getenv("GOOGLE_CREDENTIALS")
        self.credentials = self._authenticate()
        self.last_update_time = datetime.datetime.now(datetime.timezone.utc)
        self.compass_tool = CompassTool()
        self.compass_index = "google-drive-files"
        self.file_ids = set()

    def _build_drive_service(self):
        """Build a drive service for the user"""
        return build("drive", "v3", credentials=self._authenticate())

    def _authenticate(self):
        """Authenticate the user"""
        if self.credentials and not self.credentials.expired:
            return self.credentials
        elif self.credentials and self.credentials.expired:
            self.credentials.refresh(Request())
            return self.credentials
        elif os.path.exists("token.pickle"):
            with open(f"token_{self.user_id}.pickle", "rb") as token:
                self.credentials = pickle.load(token)
                return self.credentials
        else:
            # Redo authentication
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            self.credentials = flow.run_local_server(port=0)
            # Fetch user_id
            people_service = build("people", "v1", credentials=self.credentials)
            user_info = (
                people_service.people()
                .get(resourceName="people/me", personFields="metadata")
                .execute()
            )
            self.user_id = user_info["metadata"]["sources"][0]["id"]
            # Save the credentials for the next run
            with open(f"token_{self.user_id}.pickle", "wb") as token:
                pickle.dump(self.credentials, token)
            return self.credentials

    def search_gdrive(self, query: str, count: int = 30):
        """Search for files in Google Drive and return top `count` results"""
        search_query = self._build_search_query(query)
        service = self._build_drive_service()
        query_fields = "files(id, name, mimeType, "
        query_fields += "permissions(id, displayName, type), modifiedTime)"
        results = (
            service.files()
            .list(
                q=search_query,
                spaces="drive",
                fields=query_fields,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                pageSize=count,
            )
            .execute()
        )
        return results.get("files", [])

    def _download_file(file_id, output_path):
        """Download file from Google Drive and store to output path"""
        # TODO: Implement this
        pass

    def _batch_download_files(self, file_ids, output_dir):
        """Batch download files from Google Drive"""
        # TODO: Implement this
        pass

    def search_compass(self, query, user_id):
        """Search Compass for query with user_id filter"""
        self.compass_tool.call(
            parameters={
                "action": "search",
                "index": self.compass_index,
                "query": query,
                "filters": [],  # TODO: Add user_id filter
            }
        )

    def _build_search_query(self, query):
        words = word_tokenize(query)
        stop_words = set(stopwords.words("english"))
        filtered_words = [word for word in words if word.lower() not in stop_words]
        search_conditions = [
            "("
            + " or ".join(
                [f"mimeType = '{mime_type}'" for mime_type in ALLOWED_FILE_TYPES]
            )
            + ")",
            "("
            + " or ".join([f"fullText contains '{word}'" for word in filtered_words])
            + ")",
        ]
        search_query = " and ".join(search_conditions)
        return search_query

    def call(self, parameters, **kwargs):
        query = parameters.get("query", None)
        if not query:
            logger.error(
                "Google Drive Tool: No search query specified. "
                "No action will be taken. "
                f"Parameters specified: {parameters}"
            )
            return []
        top_k = parameters.get("top_k", 10)
        # Search for files in Google Drive
        drive_results = self.search_gdrive(
            query=query, count=DRIVE_SEARCH_MULTIPLE * top_k
        )
        # Check if files have been modified since the last update time
        for file in drive_results:
            modified_time = datetime.datetime.fromisoformat(file["modifiedTime"])
            if (modified_time > self.last_update_time) or (
                file["id"] not in self.file_ids
            ):
                # File has been modified since the last update time
                # Download the file and update in Compass
                output_file = (
                    "tmp"  # TODO: Use temporary directory to store the downloaded file
                )
                self._download_file(file["id"], output_file)
                self.compass_tool.call(
                    parameters={
                        "action": "update",
                        "index": self.compass_index,
                        "file_id": file["id"],
                        "file_path": output_file,
                        # TODO: Add user_id in custom_context field
                        "custom_context": {},
                    }
                )
        # Search Compass with the query
        compass_results = self.compass_tool.call(
            parameters={
                "action": "search",
                "index": self.compass_index,
                "query": query,
                "top_k": COMPASS_SEARCH_MULTIPLE * top_k,
            }
        )
        # For each of the files returned by Compass, check if it exist in Google Drive
        # or have been modified since the last update time.
        for file in compass_results:
            service = self._build_drive_service()
            request = service.file().get(fileId=file["id"]).execute()
            modified_time = datetime.datetime.fromisoformat(request["modifiedTime"])
            if request.get("error", None):
                # File does not exist in Google Drive
                # Delete the file from Compass
                self.compass_tool.call(
                    parameters={
                        "action": "delete",
                        "index": self.compass_index,
                        "file_id": file["id"],
                    }
                )
            elif modified_time > self.last_update_time:
                # File has been modified in Google Drive
                # Download the file and update in Compass
                output_file = 0  # TODO:
                self._download_file(file["id"], output_file)
                self.compass_tool.call(
                    parameters={
                        "action": "update",
                        "index": self.compass_index,
                        "file_id": file["id"],
                        "file_path": output_file,
                        # TODO: Add user_id in custom_context field
                        "custom_context": {},
                    }
                )
        # Update the last update time to current
        self.last_update_time = datetime.datetime.now(datetime.timezone.utc)
        # Apply recency filter to the top_k Compass results
        results = []
        TIME_THRESHOLD = datetime.timedelta(hours=1)
        for file in compass_results:
            service = self._build_drive_service()
            request = service.file().get(fileId=file["id"]).execute()
            modified_time = datetime.datetime.fromisoformat(request["modifiedTime"])
            if modified_time > self.last_update_time - TIME_THRESHOLD:
                results.append(file)
        return results[:top_k]
