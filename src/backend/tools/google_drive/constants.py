CSV_MIMETYPE = "text/csv"
TEXT_MIMETYPE = "text/plain"
SEARCH_LIMIT = 5
COMPASS_UPDATE_INTERVAL = 86400
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
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
SEARCH_MIME_TYPES = NATIVE_SEARCH_MIME_TYPES + NON_NATIVE_SEARCH_MIME_TYPES
DOC_FIELDS = "id, name, mimeType, webViewLink, lastModifyingUser, modifiedTime, exportLinks, shortcutDetails"

GOOGLE_DRIVE_TOOL_ID = "google_drive"
