const { loadPyodide } = require("pyodide");
const functions = require('@google-cloud/functions-framework');
const express = require('express');
const delay = (t, val) => new Promise(resolve => setTimeout(resolve, t, val));
const fs = require('fs').promises;
const path = require('path');


// load up which environment we need to be in.
const ENVIRONMENT = {
    LOCAL : "local",
    DOCKER: "docker",
    GCP_CLOUD_FUNCTION: "gcp_cloud_function",
}

const currentEnv = process.env.ENV_RUN_AS || ENVIRONMENT.GCP_CLOUD_FUNCTION;

console.log("Running in environment:", currentEnv);

// pre-load pyodide to not take the ~2s latency hit during the user req. 
// (but we re-create the environment after every call so as to not leave a trace and scrub data)
let pyodide = null;
let out_string = ""
let err_string = ""
const pythonEnvironmentHomeDir = "/home/earth";

let default_files = []
let default_file_names = new Set()
const default_directory_outer_path = 'default_python_home';

/**
 * Creates the environment for running Pyodide.
 * @returns {Promise} A promise that resolves when Pyodide is loaded.
 */
const create_env = () => {
    out_string = ""
    err_string = ""
    pyodide = null
    return loadPyodide({
        packageCacheDir: "pyodide_cache", // allows us to cache the packages in the cloud function deployment
        stdout: msg => { out_string += msg + "\n" },
        stderr: msg => { err_string += msg + "\n" },
        jsglobals: {
            clearInterval, clearTimeout, setInterval, setTimeout,
            // the following need some explanation:
            // we need to provide a fake ImageData & document object to pyodide, because matplotlib-pyodide polyfills try to access them when initializing
            // BUT luckily for us matplotlib-pyodide does not actually use them for .savefig rendering (only for .show()), so we can just provide empty objects
            ImageData: {}, document: {
                getElementById: (id) => {
                    if (id.includes("canvas")) return null; // lol don't ask ... this is needed! https://github.com/pyodide/matplotlib-pyodide/blob/61935f72718c0754a9b94e1569a685ad3c50ae91/matplotlib_pyodide/wasm_backend.py#L48
                    else return {
                        addEventListener: () => { },
                        style: {},
                        classList: { add: () => { }, remove: () => { } },
                        setAttribute: () => { },
                        appendChild: () => { },
                        remove: () => { },
                    }
                },
                createElement: () => ({
                    addEventListener: () => { },
                    style: {},
                    classList: { add: () => { }, remove: () => { } },
                    setAttribute: () => { },
                    appendChild: () => { },
                    remove: () => { },
                }),
                createTextNode: () => ({
                    addEventListener: () => { },
                    style: {},
                    classList: { add: () => { }, remove: () => { } },
                    setAttribute: () => { },
                    appendChild: () => { },
                    remove: () => { },
                }),
                body: {
                    appendChild: () => { },
                },
            }
        }, // removing any way for python to access any of the hosts js functions or variables
        homedir: pythonEnvironmentHomeDir // using a non-descriptive home dir
    }
    ).then(r => {
        pyodide = r // we do this slightly convoluted assignment, because we can't have top-level awaits!
        console.log("Pyodide base is loaded")
        // write the default files from default_python_home to the pyodide file system
        default_files.forEach((f) => {
            pyodide.FS.writeFile(pyodide.PATH.join2(pythonEnvironmentHomeDir, f.filename), f.byte_data);
        })
        // load the packages we commonly use to avoid the latency hit during the user req
        return pyodide.loadPackage(["numpy", "matplotlib", "pandas"])
    }).then(() => {
        // second part of the import (also takes a latency hit), its ok to re-import packages
        return pyodide.runPythonAsync("import matplotlib.pyplot as plt\nimport pandas as pd\nimport numpy as np")
    }).then(() => {
        console.log("Pyodide is loaded with packages imported")
        return true
    })
}

/**
 * Simple helper function to read a file asynchronously.
 * @param {string} filePath - The path of the file to be read.
 * @returns {Promise<{ filename: string, data: Buffer }>} - A promise that resolves to an object containing the filename and the file data.
 * @throws {Error} - If there is an error reading the file.
 */
function readHostFileAsync(filePath) {
    return fs.readFile(filePath)
        .then(data => {
            return { filename: path.basename(filePath), data };
        })
        .catch(err => {
            throw new Error(`Error reading file ${filePath}: ${err}`);
        });
}

//
// STARTUP: load the default files from the default_python_home directory & start the pyodide environment
//
fs.readdir(default_directory_outer_path).then(files => {
    const filePromises = files.map(file => {
        const filePath = path.join(default_directory_outer_path, file);
        return readHostFileAsync(filePath);
    });
    return Promise.all(filePromises);
}).then(filesData => {
    filesData.forEach(({ filename, data }) => {
        default_files.push({ "filename": filename, "byte_data": new Uint8Array(data) })
        default_file_names.add(filename)
    });

    //
    // NOW start the pyodide environment
    //
    create_env()
})

/**
 * Function to recursively list files in the pyodide file system from the given directory.
 * @param {string} dir 
 * @returns list of file paths
 */
function listFilesRecursive(dir) {
    var files = [];
    var entries = pyodide.FS.readdir(dir);

    for (var i = 0; i < entries.length; i++) {
        var entry = entries[i];
        if (entry === '.' || entry === '..') {
            // Skip entries that are themselves directories
            continue;
        }
        if (default_file_names.has(entry)) {
            // Skip default files
            continue;
        }
        var fullPath = pyodide.PATH.join2(dir, entry);

        if (pyodide.FS.isDir(pyodide.FS.stat(fullPath).mode)) {
            // If it's a directory, recursively list files in that directory
            files = files.concat(listFilesRecursive(fullPath));
        } else {
            // If it's a file, add it to the list
            files.push(fullPath);
        }
    }

    return files;
}

/**
 * Reads a file from the pyodide file system from the given file path and returns its content as a base64 encoded string.
 * @param {string} filePath - The path of the file to be read.
 * @returns {string} - The base64 encoded content of the file.
 */
function readFileAsBase64(filePath) {
    var fileData = pyodide.FS.readFile(filePath, { encoding: 'binary' });
    return bytesToBase64(fileData);
}

/**
 * transforms a base64 encoded string into a byte array.
 * @param {string} base64 
 * @returns Uint8Array of bytes
 */
function base64ToBytes(base64) {
    const binString = atob(base64);
    return Uint8Array.from(binString, (m) => m.codePointAt(0));
}

/**
 * Transforms a byte array into a base64 encoded string.
 * @param {Uint8Array} bytes the raw bytes to encode as base64
 * @returns base64 encoded string
 */
function bytesToBase64(bytes) {
    const binString = String.fromCodePoint(...bytes);
    return btoa(binString);
}

//
// The main http endpoint 
//
// Can create more express apps if we need multiple services.
const terrariumApp = express();
terrariumApp.use(express.json());
// add route here if we need to have multiple endpoints.
terrariumApp.post('', async (req, res) => {
     // make sure pyodide is loaded
     res.setHeader("Content-Type", "application/json");
     if (pyodide == null) {
         console.warn("pyodide not yet loaded")
         let max_tries = 0
         while (max_tries < 100 && pyodide == null) {
             await delay(100);
             max_tries++;
         }
         if (pyodide == null) {
             console.error("pyodide is still not loaded after waiting")
             res.send(JSON.stringify({ "success": false, "error": "service not ready" }));
             return
         }
         console.warn("pyodide loaded with delay", max_tries * 100, "ms")
     }
 
     const start_code = Date.now();
 
     //
     // parse the request body (code & files)
     //
     console.log("Request body:", req.body)
     const code = req.body.code
     if (code == undefined || code.trim() == "") {
         res.send(JSON.stringify({ "success": false, "error": { "type": "parsing", "message": "no code provided" } }) + "\n");
         return
     }
     let files = [] // { "filename": "file.txt", "b64_data": "dGhlc..." }]
     if (req.body.files != undefined) {
         files = req.body.files
         console.log("Got " + files.length + " input files")
         console.log(files.map(f => f.filename + " " + f.b64_data.slice(0, 10) + "... " + f.b64_data.length))
     }
 
     let return_obj = {
         //"code": code
     }
 
     try {
         // load available and needed packages - only supports pyodide built-in packages
         await pyodide.loadPackagesFromImports(code)
 
         //
         // write the input files to the pyodide file system
         //
         files.forEach((f) => {
             if (f.filename == undefined || f.b64_data == undefined) {
                 res.send(JSON.stringify({ "success": false, "error": { "type": "parsing", "message": "file data is missing for: " + JSON.stringify(f) } }) + "\n");
                 return
             }
             // TODO make sure to create subdirectories if the file is in a subdirectory path
             pyodide.FS.writeFile(pyodide.PATH.join2(pythonEnvironmentHomeDir, f.filename), base64ToBytes(f.b64_data));
         })
 
         //
         // !! here is where the code is actually executed !!
         //
         let result = await pyodide.runPythonAsync(code)
 
         //
         // soak up newly created files and return them as output
         //
         var allFiles = listFilesRecursive(pythonEnvironmentHomeDir);
 
         // get only the new files (not in the input files) and read as base64
         let input_file_names = files.map(f => f.filename)
         let new_files = allFiles
             .filter(f => !input_file_names.includes(f.slice(pythonEnvironmentHomeDir.length + 1)))
             .map(f => {
                 return { "filename": f.slice(pythonEnvironmentHomeDir.length + 1), "b64_data": readFileAsBase64(f) } //"content": decodeBase64ToText(readFileAsBase64(f))
             })
         console.log("output files:", new_files.map(f => f.filename + " " + f.b64_data.slice(0, 10) + "... " + f.b64_data.length))
         return_obj.output_files = new_files
 
         result_reporting = ""
         if (result != undefined) {
             result_reporting = result.toString().replace(/\n/g, '\\n')
         }
         console.log("[Success] Code:", code.replace(/\n/g, '\\n'),
             "final_expression:", result_reporting,
             "stdout:", out_string.replace(/\n/g, '\\n'),
             "stderr:", err_string.replace(/\n/g, '\\n'))
 
         return_obj.final_expression = result
         return_obj.sucess = true
 
     } catch (error) {
         console.error("[Failure] Code:", code.replace(/\n/g, '\\n'),
             "Error:", error.toString().replace(/\n/g, '\\n'))
 
         return_obj.error = { "type": error.type, "message": error.toString() }
         return_obj.sucess = false
     }
 
     return_obj.std_out = out_string
     return_obj.std_err = err_string
     return_obj["code_runtime"] = (Date.now() - start_code)
 
     // write out the answer, but do not close the response yet - otherwise gcp cloud functions terminate the cpu cycles and hibernate the recycling
     res.write(JSON.stringify(return_obj) + "\n");
 
     console.log("Reloading pyodide")
 
     // run the recycle background process'
     // see https://cloud.google.com/functions/docs/bestpractices/tips#do_not_start_background_activities
     await create_env()
 
     // to make gcp run it until the promise resolves & only now close the response connection
     res.end()
});

if(currentEnv === ENVIRONMENT.GCP_CLOUD_FUNCTION) {
    exports.terrarium = functions.http("terrarium", terrariumApp);
}
else {
    terrariumApp.listen(8080, () => {
        console.log("Server is running on port 8080");
    });
}
