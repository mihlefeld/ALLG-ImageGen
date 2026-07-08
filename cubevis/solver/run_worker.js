// Node.js bridge for cubevis/solver/worker.js
//
// Reads a single JSON object from stdin (matching the `input` parameter of
// worker.js's main()), shims `self` and `postMessage`, then loads worker.js
// and dispatches the input to `self.onmessage`. Every message the worker
// posts is written to stdout as one JSON object per line.
//
// Special-cases: Map instances (only the `moveWeights` message carries one)
// are serialised as arrays of [key, value] pairs so they survive JSON.

const path = require("path");

function encodeValue(v) {
    if (v instanceof Map) {
        return Array.from(v.entries());
    }
    return v;
}

global.self = {};
global.postMessage = function (msg) {
    const out = { type: msg.type, value: encodeValue(msg.value) };
    process.stdout.write(JSON.stringify(out) + "\n");
};

// Loading worker.js executes its top-level code, which assigns self.onmessage.
require(path.join(__dirname, "worker.js"));

let stdinData = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => { stdinData += chunk; });
process.stdin.on("end", () => {
    let input;
    try {
        input = JSON.parse(stdinData);
    } catch (e) {
        process.stderr.write("Failed to parse input JSON: " + e.message + "\n");
        process.exit(2);
    }
    if (typeof self.onmessage !== "function") {
        process.stderr.write("worker.js did not register self.onmessage\n");
        process.exit(3);
    }
    try {
        self.onmessage({ data: input });
    } catch (e) {
        process.stderr.write("Worker main threw: " + (e && e.stack ? e.stack : String(e)) + "\n");
        process.exit(4);
    }
    process.exit(0);
});
