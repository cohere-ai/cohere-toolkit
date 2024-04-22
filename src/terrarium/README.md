# Terrarium - A Python Sandbox

Terrarium is a relatively low latency, easy to use, and economical Python sandbox - to be used as a gcp cloud function - for executing untrusted user or LLM generated `python` code.

_Written and maintained by @sebastian-hofstaetter._

- **Terrarium is fast:** 900ms e2e runtime to generate a 200 dpi png with a simple matplotlib barchart - 500 ms for a svg version. (hosted on GCP cloud functions)
- **Terrarium is cheap:** We spent less than $30 a month hosting terrarium as a GCP cloud function during internal annotations (2GB mem + 1vCPU and at least 1 alive instance + autoscale on demand)
- **Terrarium is fully compartmentalized:** The sandbox gets completely recycled after every invocation. No state whatsoever is carried over between calls. _Cohere does not give any guarantees for the sandbox integrity._
- **Terrarium supports native input & output files:** You can send any number & type of files as part of the request and we put it them in the python filesystem. After the code execution we gather up all generated files and return them with the response.
- **Terrarium supports most common packages:** Terrarium runs on [Pyodide](https://pyodide.org/en/stable/index.html), therefore it supports numpy, pandas, matplotlib, sympy, and other standard python packages.

## Using Terrarium

Using the deployed cloud function is super easy - just call it with the `code` to run & authorization bearer (if so configured) as follows:

```bash
curl -X POST --url https://{{GCP_REGION}}-{{GCP_PROJECT_ID}}.cloudfunctions.net/terrarium \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
--no-buffer \
--data-raw '{"code": "1 + 1"}'
```

which returns:

```json
{
  "output_files": [],
  "final_expression": 2,
  "sucess": true,
  "std_out": "",
  "std_err": "",
  "code_runtime": 16
}
```

The authentication `gcloud auth print-identity-token` needs to be renewed every hour.

See `terrarium_client.py` for an easy-to-use python function to call the service - including file input & output functionality via base64 encoded files.

## Sandbox Design

The sandbox is composed of multiple layers:

1. Parse, compile, & execute python code inside a node.js process - via CPython compiled to webassembly, not running natively - with https://pyodide.org/en/stable/index.html. This approach restricts the untrusted code's abilities:

   - NO access to the filesystem (pyodide provides a compartmentalized memory only guest filesystem)
   - NO threading & multiprocessing
   - NO ability to call a subprocess
   - NO access to any of our hosts memory
   - NO access to other call states: we recycle the full pyodide environment (including the virtual file system, global state, loaded libs ... the works) after every call
   - NO network nor internet access

2. Deploy the node.js host into a GCP cloud function, which restricts:
   - runtime
   - decouples the node.js host (in case of a breakout) from our VMs (afaik gcp cloud functions do not have access to the project's vpc network if not actively granted with connectors)

It is very hard to restrict python capabilities in pure CPython (see: https://stackoverflow.com/a/62661311), therefore the route of using pyodide should _fingers crossed_ be better & the more robust sandbox. For additional security we rely on the GCP cloud functions sandbox as a second layer.

---

The following packages are supported out of the box:
https://pyodide.org/en/stable/usage/packages-in-pyodide.html including, but not limited to:

- numpy
- pandas
- sympy
- beautifulsoup4
- matplotlib (plt.show() is not supported, but plt.savefig() works like a charm)
- python-sat
- scikit-learn
- scipy
- sqlite3 (not enabled by default, but we could load it as well)

## Development

You need node.js installed on your system. To install dependencies run:

```bash
npm install
mkdir pyodide_cache
```

run the server & function locally:

```bash
npx @google-cloud/functions-framework --target=terrarium --port=1234
```

execute code in the terrarium:

```bash
curl -X POST -H "Content-Type: application/json" \
--url http://localhost:1234 \
--data-raw '{"code": "1 + 1"}' \
--no-buffer
```

run a set of test files (all .py files in `/test`) through the endpoint with:

```bash
python terrarium_client.py
```

## Deploying to GCP

Deploy a gen2 node.js function (https://cloud.google.com/functions/docs/create-deploy-http-nodejs)

Make sure you have populated the local pyodide_cache with .whl files before running the deploy. We recommend a minimum of 2GB and 1 vCPU for the deployed runtime.

```
gcloud functions deploy terrarium \
  --gen2 \
  --runtime=nodejs20 \
  --region=us-central1 \
  --source=. \
  --entry-point=terrarium \
  --trigger-http \
  --ingress-settings=internal-only
```

## Limitations

For large & complex computations we sometimes observe untraceble "RangeError: Maximum call stack size exceeded" exceptions.

- This increasingly happens when we set a too high dpi parameter on png saves for matplotlib figures
- Or highly complex pandas operations

See also: https://blog.pyodide.org/posts/function-pointer-cast-handling/
