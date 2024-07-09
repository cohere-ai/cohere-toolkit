CSV_MIMETYPE = "text/csv"
TEXT_MIMETYPE = "text/plain"
SEARCH_LIMIT = 5
COMPASS_UPDATE_INTERVAL = 86400
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]
SEARCH_MIME_TYPES = [
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.spreadsheet",
    "application/vnd.google-apps.presentation",
    "application/vnd.google-apps.shortcut",
    # "application/pdf",
]
DOC_FIELDS = "id, name, mimeType, webViewLink, lastModifyingUser, modifiedTime, exportLinks, shortcutDetails"

GOOGLE_DRIVE_TOOL_ID = "google_drive"
