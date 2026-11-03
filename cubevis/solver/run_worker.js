// Node.js bridge for the BatchSolver2 web worker.
//
// Reads one JSON input object from stdin, shims the browser APIs used by the
// worker, and writes each posted message as JSONL.

const path = require("path");
const { pathToFileURL } = require("url");
const { readFile } = require("fs/promises");

const batchSolverDir = path.resolve(
    __dirname,
    "../../trangium.github.io/BatchSolver2"
);

async function main() {
    let inputText = "";
    for await (const chunk of process.stdin) {
        inputText += chunk;
    }

    let input;
    try {
        input = JSON.parse(inputText);
    } catch (e) {
        throw new Error("Failed to parse input JSON: " + e.message);
    }
    if (!input || input.puzzle === undefined) {
        throw new Error("Worker input must include a puzzle definition.");
    }

    let resolveWorkerDone;
    const workerDone = new Promise((resolve) => {
        resolveWorkerDone = resolve;
    });
    global.self = {
        postMessage(msg) {
            process.stdout.write(JSON.stringify(msg) + "\n");
            if (msg.type === "stop") resolveWorkerDone();
        },
    };

    const nativeFetch = global.fetch;
    global.fetch = async (resource, ...args) => {
        const url = resource instanceof URL ? resource : new URL(resource);
        if (url.protocol !== "file:") return nativeFetch(resource, ...args);
        try {
            const text = await readFile(url, "utf8");
            return { ok: true, status: 200, text: async () => text };
        } catch (e) {
            if (e.code !== "ENOENT") throw e;
            return { ok: false, status: 404, text: async () => "" };
        }
    };

    const workerUrl = pathToFileURL(
        path.join(batchSolverDir, "worker.js")
    ).href;
    await import(workerUrl);
    if (typeof self.onmessage !== "function") {
        throw new Error("BatchSolver2 worker.js did not register self.onmessage.");
    }

    const result = self.onmessage({ data: input });
    if (result && typeof result.then === "function") await result;
    await workerDone;
}

main().catch((e) => {
    process.stderr.write((e && e.stack ? e.stack : String(e)) + "\n");
    process.exitCode = 1;
});
