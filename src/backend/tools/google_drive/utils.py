from .constants import CSV_MIMETYPE, TEXT_MIMETYPE


def extract_links(files):
    id_to_urls = dict()
    for _file in files:
        export_links = _file.pop("exportLinks", {})
        id = _file.get("id")
        if id is None:
            continue

        if TEXT_MIMETYPE in export_links:
            id_to_urls[id] = export_links[TEXT_MIMETYPE]
        elif CSV_MIMETYPE in export_links:
            id_to_urls[id] = export_links[CSV_MIMETYPE]
    return id_to_urls
