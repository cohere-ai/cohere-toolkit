from enum import Enum

CSV_MIMETYPE = "text/csv"
TEXT_MIMETYPE = "text/plain"
SEARCH_LIMIT = 5
# TODO dev only: revert to 86400
ACTIVITY_TRACKING_WINDOW = 86400 * 7
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.activity.readonly",
]
NATIVE_SEARCH_MIME_TYPES = [
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.spreadsheet",
    "application/vnd.google-apps.presentation",
]
NON_NATIVE_SEARCH_MIME_TYPES = [
    "application/vnd.google-apps.shortcut",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/pdf",
    "text/plain",
    "text/markdown",
]
NATIVE_EXTENSION_MAPPINGS = {
    "application/vnd.google-apps.document": "txt",
    "application/vnd.google-apps.spreadsheet": "csv",
    "application/vnd.google-apps.presentation": "pptx",
}
SEARCH_MIME_TYPES = NATIVE_SEARCH_MIME_TYPES + NON_NATIVE_SEARCH_MIME_TYPES
DOC_FIELDS = "id, name, mimeType, webViewLink, exportLinks, shortcutDetails, trashed, parents, fileExtension, permissions"

GOOGLE_DRIVE_TOOL_ID = "google_drive"


class GoogleDriveActions(Enum):
    CREATE = "create"
    EDIT = "edit"
    MOVE = "move"
    RENAME = "rename"
    DELETE = "delete"
    RESTORE = "restore"
    PERMISSION_CHANGE = "permission_change"
