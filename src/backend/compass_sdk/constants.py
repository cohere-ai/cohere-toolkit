DEFAULT_MAX_CHUNKS_PER_REQUEST = 100
DEFAULT_SLEEP_RETRY_SECONDS = 5
DEFAULT_MAX_RETRIES = 1
DEFAULT_MAX_ERROR_RATE = 0.5
DEFAULT_MAX_ACCEPTED_FILE_SIZE_BYTES = 50_000_000

DEFAULT_MIN_CHARS_PER_ELEMENT = 3
DEFAULT_NUM_TOKENS_PER_CHUNK = 500
DEFAULT_NUM_TOKENS_CHUNK_OVERLAP = 15
DEFAULT_MIN_NUM_TOKENS_CHUNK = 5
DEFAULT_MAX_TOKENS_METADATA = 50
DEFAULT_MIN_NUM_CHUNKS_IN_TITLE = 1

DEFAULT_WIDTH_HEIGHT_VERTICAL_RATIO = 0.6
NUM_ADDITIONAL_CHARS_FOR_METADATA = 100
SKIP_INFER_TABLE_TYPES = ["jpg", "png", "xls", "xlsx", "heic"]

# Metadata detection constants
DEFAULT_COMMANDR_EXTRACTABLE_ATTRIBUTES = ["title", "authors", "date"]
DEFAULT_COMMANDR_PROMPT = """
        Given the following document:
        {text}. 
        Extract the following attributes from the document: {attributes}. 
        Write the output in JSON format. For example, if the document title is "Hello World" 
        and the authors are "John Doe" and "Jane Smith", the output should be:
        {{"title": "Hello World", "authors": ["John Doe", "Jane Smith"]}}. 
        Do not write the ```json (...) ``` tag. The output should be a valid JSON.  
        If you cannot find the information, write "" for the corresponding field. 
        Answer:
        """
METADATA_HEURISTICS_ATTRIBUTES = [
    "title",
    "name",
    "date",
    "authors",
]
