#!/usr/bin/env node
// Lokaler MCP-Server (stdio, ohne Zusatzpakete, Node 18+) für die Lexware Office-API.
// Der API-Schlüssel kommt aus der Umgebungsvariable LEXWARE_API_KEY oder aus
// ~/.config/lexware-skill/api-key (wird mit lexware_set_api_key gespeichert, chmod 600).
import { readFileSync, writeFileSync, mkdirSync, existsSync, chmodSync, statSync } from "node:fs";
import { homedir } from "node:os";
import { join, basename, extname } from "node:path";
import { createInterface } from "node:readline";

const CFG = {
  name: "Lexware Office",
  prefix: "lexware",
  base: process.env.LEXWARE_API_KEY_BASE_URL || "https://api.lexware.io",
  env: "LEXWARE_API_KEY",
  keyDir: join(homedir(), ".config", "lexware-skill"),
  authHeader: (k) => ("Bearer " + k),
  statusPath: "/v1/profile",
  minGapMs: 550,
  upload: { path: "/v1/files", fileField: "file", fields: { type: "voucher" } },
};
const KEY_FILE = join(CFG.keyDir, "api-key");

function apiKey() {
  const fromEnv = (process.env[CFG.env] || "").trim();
  if (fromEnv && !fromEnv.startsWith("${")) return fromEnv;
  if (existsSync(KEY_FILE)) return readFileSync(KEY_FILE, "utf8").trim();
  return "";
}

let last = 0;
async function gap() {
  const wait = CFG.minGapMs - (Date.now() - last);
  if (wait > 0) await new Promise((r) => setTimeout(r, wait));
  last = Date.now();
}

async function call(method, path, { query, body, form, accept = "application/json" } = {}) {
  const key = apiKey();
  if (!key) throw new Error(`Kein API-Schlüssel. Bitte mit ${CFG.prefix}_set_api_key speichern.`);
  if (!path.startsWith("/")) path = "/" + path;
  const url = new URL(CFG.base + path);
  for (const [k, v] of Object.entries(query || {})) url.searchParams.set(k, String(v));
  const headers = { Accept: accept, Authorization: CFG.authHeader(key) };
  let payload;
  if (form) payload = form;
  else if (body !== undefined && body !== null) {
    headers["Content-Type"] = "application/json";
    payload = typeof body === "string" ? body : JSON.stringify(body);
  }
  for (let attempt = 0; attempt < 4; attempt++) {
    await gap();
    const res = await fetch(url, { method, headers, body: payload });
    if (res.status === 429 && attempt < 3) {
      await new Promise((r) => setTimeout(r, 1500 * (attempt + 1)));
      continue;
    }
    if (accept !== "application/json") {
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${(await res.text()).slice(0, 2000)}`);
      return Buffer.from(await res.arrayBuffer());
    }
    const text = await res.text();
    if (!res.ok) throw new Error(`HTTP ${res.status} bei ${method} ${path}: ${text.slice(0, 2000)}`);
    return text ? JSON.parse(text) : {};
  }
}

const TOOLS = [
  {
    name: `${CFG.prefix}_status`,
    description: `Prüft, ob ein ${CFG.name}-API-Schlüssel gespeichert ist und die Verbindung klappt. Zuerst aufrufen.`,
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: `${CFG.prefix}_set_api_key`,
    description: `Speichert den ${CFG.name}-API-Schlüssel lokal auf diesem Rechner (nur lesbar für den Benutzer). Den Schlüssel danach nie wiederholen.`,
    inputSchema: { type: "object", properties: { api_key: { type: "string" } }, required: ["api_key"] },
  },
  {
    name: `${CFG.prefix}_request`,
    description: `Beliebiger Aufruf der ${CFG.name}-API. path z. B. "/v1/voucherlist". body als JSON-Objekt. Gibt die JSON-Antwort zurück.`,
    inputSchema: {
      type: "object",
      properties: {
        method: { type: "string", enum: ["GET", "POST", "PUT", "DELETE"] },
        path: { type: "string" },
        query: { type: "object", additionalProperties: { type: ["string", "number", "boolean"] } },
        body: { type: ["object", "array", "null"] },
      },
      required: ["method", "path"],
    },
  },
  {
    name: `${CFG.prefix}_upload_voucher`,
    description: `Lädt eine Belegdatei (pdf, jpg, png, max. 5 MB) von diesem Rechner zu ${CFG.name} hoch.`,
    inputSchema: { type: "object", properties: { file_path: { type: "string" } }, required: ["file_path"] },
  },
  {
    name: `${CFG.prefix}_download_pdf`,
    description: `Lädt ein PDF (z. B. Rechnung) und speichert es auf diesem Rechner. path ist der API-Pfad zur Datei, target_path der Zielpfad.`,
    inputSchema: {
      type: "object",
      properties: { path: { type: "string" }, target_path: { type: "string" } },
      required: ["path", "target_path"],
    },
  },
];

async function runTool(name, args = {}) {
  const p = CFG.prefix;
  if (name === `${p}_status`) {
    if (!apiKey()) return `Kein API-Schlüssel gespeichert. Mit ${p}_set_api_key speichern.`;
    const res = await call("GET", CFG.statusPath);
    return "Verbunden. " + JSON.stringify(res).slice(0, 1500);
  }
  if (name === `${p}_set_api_key`) {
    const k = String(args.api_key || "").trim();
    if (k.length < 10) throw new Error("Das sieht nicht nach einem gültigen Schlüssel aus.");
    mkdirSync(CFG.keyDir, { recursive: true });
    writeFileSync(KEY_FILE, k + "\n", { mode: 0o600 });
    chmodSync(KEY_FILE, 0o600);
    return `Gespeichert in ${KEY_FILE}.`;
  }
  if (name === `${p}_request`) {
    const res = await call(String(args.method || "GET").toUpperCase(), String(args.path), {
      query: args.query,
      body: args.body ?? undefined,
    });
    return JSON.stringify(res, null, 2);
  }
  if (name === `${p}_upload_voucher`) {
    const fp = String(args.file_path);
    const ext = extname(fp).toLowerCase();
    const types = { ".pdf": "application/pdf", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".xml": "application/xml" };
    if (!types[ext]) throw new Error("Nur pdf, jpg, png oder xml.");
    if (statSync(fp).size > 5 * 1024 * 1024) throw new Error("Datei größer als 5 MB, bitte verkleinern.");
    const form = new FormData();
    for (const [k, v] of Object.entries(CFG.upload.fields)) form.set(k, v);
    form.set(CFG.upload.fileField, new Blob([readFileSync(fp)], { type: types[ext] }), basename(fp));
    const res = await call("POST", CFG.upload.path, { form });
    return JSON.stringify(res, null, 2);
  }
  if (name === `${p}_download_pdf`) {
    const buf = await call("GET", String(args.path), { accept: "application/pdf" });
    writeFileSync(String(args.target_path), buf);
    return `Gespeichert: ${args.target_path} (${buf.length} Bytes)`;
  }
  throw new Error(`Unbekanntes Werkzeug: ${name}`);
}

function send(msg) {
  process.stdout.write(JSON.stringify(msg) + "\n");
}

const rl = createInterface({ input: process.stdin });
rl.on("line", async (line) => {
  if (!line.trim()) return;
  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    return;
  }
  const { id, method, params } = msg;
  if (id === undefined) return; // Benachrichtigungen ignorieren
  try {
    if (method === "initialize") {
      send({
        jsonrpc: "2.0",
        id,
        result: {
          protocolVersion: params?.protocolVersion || "2025-06-18",
          capabilities: { tools: {} },
          serverInfo: { name: `${CFG.prefix}-skill`, version: "1.0.0" },
        },
      });
    } else if (method === "ping") {
      send({ jsonrpc: "2.0", id, result: {} });
    } else if (method === "tools/list") {
      send({ jsonrpc: "2.0", id, result: { tools: TOOLS } });
    } else if (method === "tools/call") {
      try {
        const text = await runTool(params?.name, params?.arguments || {});
        send({ jsonrpc: "2.0", id, result: { content: [{ type: "text", text }] } });
      } catch (e) {
        send({ jsonrpc: "2.0", id, result: { content: [{ type: "text", text: "FEHLER: " + e.message }], isError: true } });
      }
    } else {
      send({ jsonrpc: "2.0", id, error: { code: -32601, message: `Methode nicht unterstützt: ${method}` } });
    }
  } catch (e) {
    send({ jsonrpc: "2.0", id, error: { code: -32603, message: e.message } });
  }
});
