from fastapi import Request


def get_deployment_config(request: Request) -> dict:
    headers = request.get("headers", {})
    header = get_header_value(headers, ["deployment-config", "Deployment-Config"])
    config = {}
    for c in header.split(";"):
        kv = c.split("=")
        if len(kv) < 2:
            continue
        config[kv[0]] = "".join(kv[1:])
    return config


def get_header_value(headers: list, keys: list) -> str:
    for k, v in headers:
        if k.decode("utf-8") in keys:
            return v.decode("utf-8")
    return ""
