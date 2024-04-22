import base64
import glob
import json
import os
import subprocess
import time
from typing import List

import requests
from typing_extensions import TypedDict

URL = f"https://{GCP_REGION}-{GCP_PROJECT_ID}.cloudfunctions.net/terrarium"
# URL = "http://localhost:1234/"

gcp_auth_bearer = ""
gcp_auth_bearer_last_update = time.time()


def get_bearer():
    global gcp_auth_bearer
    global gcp_auth_bearer_last_update
    if gcp_auth_bearer != "" and (time.time() - gcp_auth_bearer_last_update) < 60 * 55:
        return gcp_auth_bearer
    result = subprocess.check_output(
        ["gcloud", "auth", "print-identity-token"], shell=False, text=True
    )
    # print(result)
    gcp_auth_bearer = result.strip()
    gcp_auth_bearer_last_update = time.time()
    return gcp_auth_bearer


class B64_FileData(TypedDict):
    b64_data: str
    filename: str


def run_terrarium(code: str, file_data: List[B64_FileData] = None):
    """
    Executes the given code in the terrarium environment and returns the result.

    Args:
        code (str): The code to be executed in the terrarium environment.
        file_data (dict, optional): Additional file data to be passed to the terrarium server. Defaults to None.

    Returns:
        dict: The result of executing the code in the terrarium environment.

    Raises:
        RuntimeError: If there is an error when parsing the response content.

    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": "bearer " + get_bearer(),
    }

    data = {"code": code}
    if file_data is not None:
        data["files"] = file_data

    result = requests.post(URL, headers=headers, json=data, stream=True)

    #
    # Explanation for this contorted parsing (made possbile by stream=True):
    #
    # The terrarium server needs to recycle the python interpreter environment either before or after each request.
    # We are doing it after to save on latency for the next request.
    # BUT the annoying thing is that gcp cloud functions terminate all CPU cycles as soon as the response content is closed !!
    # With this trick we can parse the response content, return from this function, but crucially don't have to close the connection,
    # and then the server can recycle the python interpreter.
    #
    res_string = ""
    try:
        for c in result.iter_content(decode_unicode=True):
            if c == "\n":
                break
            res_string += c
        return json.loads(res_string)
    except json.decoder.JSONDecodeError as e:
        raise RuntimeError("Error when parsing: " + res_string, e)


def file_to_base64(file_path):
    try:
        # Read the file in binary mode
        with open(file_path, "rb") as file:
            # Read the content of the file
            file_content = file.read()

            # Convert the binary content to base64 encoding
            base64_content = base64.b64encode(file_content)

            # Decode the base64 bytes to a UTF-8 string
            base64_string = base64_content.decode("utf-8")

            return base64_string

    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":

    test_files = glob.glob("./tests/**/*.py", recursive=True)
    for file in test_files:
        file_data = None
        if "file_io" in file:
            # load all test_file_input* files
            input_files = glob.glob("./tests/file_io/test_file_*")
            file_data = []
            for f in input_files:
                file_data.append(
                    {"filename": os.path.basename(f), "b64_data": file_to_base64(f)}
                )

        print(file)
        print("---------")
        with open(file) as f:
            code = "".join(f.readlines())
        print(code)
        print("---------")
        start = time.time()
        result = run_terrarium(code, file_data)

        if "output_files" in result:
            os.makedirs("tests/file_io/_outputs", exist_ok=True)
            for of in result["output_files"]:
                print(of["filename"], of["b64_data"][:20] + "...")
                with open(
                    os.path.join("tests/file_io/_outputs", of["filename"]), mode="wb"
                ) as f2:
                    f2.write(base64.b64decode(of["b64_data"]))

            del result["output_files"]

        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("response parsed after:", time.time() - start)
        print("\n***********************\n")
        time.sleep(15)
