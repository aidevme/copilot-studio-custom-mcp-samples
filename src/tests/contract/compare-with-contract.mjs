// compare-with-contract.mjs
// Strict check: does a server's tools/list match the tool contract exactly?
//
// check-tool-contract.js (Part 7) classifies changes between two snapshots and only fails on breaking ones.
// This script is stricter and fails on any drift: every tool in the contract must exist on the server with the
// same description and the same input schema (constraints and parameter descriptions included), and every field
// the contract defines for a tool (title, annotations, outputSchema) must match. Fields the server adds that the
// contract doesn't define are reported as warnings.
//
// Usage:  node compare-with-contract.mjs <contract.json> <tools-list.json>
// The tools/list file can be a raw result, a JSON-RPC response, or an SSE body ("data: {...}").
// Exit code 1 on any mismatch, 0 when the server matches the contract.
import { readFileSync } from "node:fs";

const [contractPath, livePath] = process.argv.slice(2);
if (!contractPath || !livePath) {
  console.error("Usage: node compare-with-contract.mjs <contract.json> <tools-list.json>");
  process.exit(2);
}

const load = (path) => {
  let text = readFileSync(path, "utf8").replace(/^﻿/, "");
  const sse = text.match(/^data: (.+)$/m);
  if (sse) text = sse[1];
  const doc = JSON.parse(text);
  const tools = doc.tools ?? doc.result?.tools ?? [];
  return new Map(tools.map((t) => [t.name, t]));
};

// Compare JSON values regardless of key order.
const canonical = (value) =>
  Array.isArray(value)
    ? value.map(canonical)
    : value && typeof value === "object"
      ? Object.fromEntries(Object.keys(value).sort().map((k) => [k, canonical(value[k])]))
      : value;
const same = (a, b) => JSON.stringify(canonical(a)) === JSON.stringify(canonical(b));

// Walk an input schema and name each difference, so the output says what to fix.
const diffSchema = (want, got, path, out) => {
  if (same(want, got)) return;
  const isObj = (v) => v && typeof v === "object" && !Array.isArray(v);
  if (!isObj(want) || !isObj(got)) {
    out.push(`${path}: contract ${JSON.stringify(want)}, server ${JSON.stringify(got)}`);
    return;
  }
  for (const key of new Set([...Object.keys(want), ...Object.keys(got)])) {
    if (!(key in got)) out.push(`${path}.${key}: in the contract, missing on the server`);
    else if (!(key in want)) out.push(`${path}.${key}: on the server, not in the contract`);
    else diffSchema(want[key], got[key], `${path}.${key}`, out);
  }
};

const contract = load(contractPath);
const live = load(livePath);
const errors = [];
const warnings = [];

for (const [name, want] of contract) {
  const got = live.get(name);
  if (!got) {
    errors.push(`${name}: in the contract, missing on the server`);
    continue;
  }
  if ((want.description ?? "") !== (got.description ?? "")) {
    errors.push(`${name}.description: contract "${want.description}", server "${got.description}"`);
  }
  diffSchema(want.inputSchema ?? {}, got.inputSchema ?? {}, `${name}.inputSchema`, errors);
  for (const key of ["title", "annotations", "outputSchema"]) {
    if (key in want && !same(want[key], got[key])) {
      errors.push(`${name}.${key}: contract ${JSON.stringify(want[key])}, server ${JSON.stringify(got[key])}`);
    } else if (!(key in want) && key in got) {
      warnings.push(`${name}.${key}: the server sets it, the contract doesn't define it`);
    }
  }
}
for (const name of live.keys()) {
  if (!contract.has(name)) errors.push(`${name}: on the server, not in the contract`);
}

for (const e of errors) console.log(`FAIL  ${e}`);
for (const w of warnings) console.log(`WARN  ${w}`);
console.log(
  errors.length === 0
    ? `PASS  the server's ${live.size} tool(s) match the contract`
    : `${errors.length} mismatch(es) between the server and ${contractPath}`,
);
process.exit(errors.length === 0 ? 0 : 1);
