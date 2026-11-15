// check-tool-contract.mjs
// Compares two MCP tools/list snapshots and classifies every difference.
// Usage: node check-tool-contract.mjs <approved.json> <candidate.json>
// Exit code 1 when a breaking change is found, 0 otherwise.
import { readFileSync } from "node:fs";

const [approvedPath, candidatePath] = process.argv.slice(2);
if (!approvedPath || !candidatePath) {
  console.error("Usage: node check-tool-contract.mjs <approved.json> <candidate.json>");
  process.exit(2);
}

const load = (path) => {
  const doc = JSON.parse(readFileSync(path, "utf8"));
  // Accept a raw tools/list result or a JSON-RPC response that wraps it.
  const tools = doc.tools ?? doc.result?.tools ?? [];
  return new Map(tools.map((t) => [t.name, t]));
};

const approved = load(approvedPath);
const candidate = load(candidatePath);
const findings = [];
const add = (level, tool, message) => findings.push({ level, tool, message });

for (const [name, oldTool] of approved) {
  const newTool = candidate.get(name);
  if (!newTool) {
    add("BREAKING", name, "tool removed");
    continue;
  }
  if ((oldTool.description ?? "") !== (newTool.description ?? "")) {
    add("REVIEW", name, "description changed (the orchestrator routes on it)");
  }
  const oldProps = oldTool.inputSchema?.properties ?? {};
  const newProps = newTool.inputSchema?.properties ?? {};
  const oldRequired = new Set(oldTool.inputSchema?.required ?? []);
  const newRequired = new Set(newTool.inputSchema?.required ?? []);

  for (const prop of Object.keys(oldProps)) {
    if (!(prop in newProps)) add("BREAKING", name, `input '${prop}' removed`);
    else if (oldProps[prop].type !== newProps[prop].type) {
      add("BREAKING", name, `input '${prop}' type ${oldProps[prop].type} -> ${newProps[prop].type}`);
    }
  }
  for (const prop of newRequired) {
    if (!oldRequired.has(prop)) add("BREAKING", name, `input '${prop}' is now required`);
  }
  for (const prop of Object.keys(newProps)) {
    if (!(prop in oldProps) && !newRequired.has(prop)) {
      add("ADDITIVE", name, `new optional input '${prop}'`);
    }
  }
}

for (const name of candidate.keys()) {
  if (!approved.has(name)) add("APPROVAL", name, "new tool: needs the approval checklist before production");
}

const order = { BREAKING: 0, APPROVAL: 1, REVIEW: 2, ADDITIVE: 3 };
findings.sort((a, b) => order[a.level] - order[b.level] || a.tool.localeCompare(b.tool));
for (const f of findings) console.log(`${f.level.padEnd(9)} ${f.tool.padEnd(18)} ${f.message}`);
if (findings.length === 0) console.log("No differences: the candidate matches the approved contract.");

process.exit(findings.some((f) => f.level === "BREAKING") ? 1 : 0);
