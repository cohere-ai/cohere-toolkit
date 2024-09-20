CSV_MIMETYPE = "text/csv"
TEXT_MIMETYPE = "text/plain"
SEARCH_LIMIT = 10
# 1 hour
ACTIVITY_TRACKING_WINDOW = 86400 / 24
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.activity.readonly",
]
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
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
