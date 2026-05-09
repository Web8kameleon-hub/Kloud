/**
 * ALBA Collector Server â€” Connected Mode
 * ------------------------------------------------------
 * Ky version i ALBA Collector lidhet direkt me backend-in e Kloud Cloud.
 * Ã‡do tÃ« dhÃ«nÃ« qÃ« vjen pÃ«rpunohet, ruhet nÃ« DB pÃ«rmes /api/telemetry
 * dhe shpÃ«rndahet te tÃ« gjithÃ« klientÃ«t nÃ« kohÃ« reale.
 *
 * Real data only â€” No mock, no random.
 */

import express, { Request, Response } from "express";
import http from "http";
import { WebSocketServer, WebSocket } from "ws";
import bodyParser from "body-parser";
import cors from "cors";
import { v4 as uuidv4 } from "uuid";

// ---------------- TYPES ----------------
type SensorType = "eeg" | "audio" | "telemetry" | "custom";

interface SensorData {
  id: string;
  type: SensorType;
  timestamp: string;
  payload: unknown;
  source?: string;
  status?: "queued" | "stored" | "failed";
}

interface BroadcastMessage {
  event: string;
  data?: unknown;
  message?: string;
}

// ---------------- CONFIG ----------------
const BACKEND_API = process.env.Kloud_BACKEND ?? "http://127.0.0.1:8001";
const PORT = Number(process.env.ALBA_PORT ?? 8010);

// ---------------- STATE ----------------
const memoryStore: SensorData[] = [];

// ---------------- APP ----------------
const app = express();
app.use(cors());
app.use(bodyParser.json({ limit: "15mb" }));

// Health
app.get("/health", async (_req: Request, res: Response) => {
  try {
    const backendHealth = await fetch(`${BACKEND_API}/health`);
    const backendData = await backendHealth.json();

    res.json({
      ok: true,
      service: "ALBA Collector",
      backend: backendData.status ?? "unknown",
      stored_entries: memoryStore.length,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("[ALBA] Backend health check failed", error);
    res.json({
      ok: false,
      service: "ALBA Collector",
      backend: "unreachable",
      stored_entries: memoryStore.length,
    });
  }
});

// Data collection
app.post("/collect", async (req: Request, res: Response) => {
  const entry: SensorData = {
    id: uuidv4(),
    type: (req.body?.type as SensorType | undefined) ?? "custom",
    timestamp: new Date().toISOString(),
    payload: req.body?.payload ?? {},
    source: req.body?.source ?? "alba-node",
    status: "queued",
  };

  memoryStore.push(entry);
  broadcast({ event: "queued", data: entry });

  try {
    const response = await fetch(`${BACKEND_API}/api/telemetry`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entry),
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const saved = (await response.json()) as Record<string, unknown>;
    entry.status = "stored";
    broadcast({ event: "stored", data: entry });

    res.json({ ok: true, id: entry.id, backend_id: saved?.id ?? null });
  } catch (error) {
    const message = error instanceof Error ? error.message : "unknown error";
    entry.status = "failed";
    broadcast({ event: "failed", data: entry });
    console.error("[ALBA] Failed to persist telemetry", error);
    res.status(500).json({ ok: false, error: message });
  }
});

// Retrieve local cache
app.get("/data", (_req: Request, res: Response) => {
  res.json({ entries: memoryStore });
});

// ---------------- WEBSOCKET ----------------
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

function broadcast(msg: BroadcastMessage) {
  const json = JSON.stringify(msg);
  wss.clients.forEach((client: WebSocket) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(json);
    }
  });
}

wss.on("connection", (ws: WebSocket) => {
  ws.send(
    JSON.stringify({
      event: "welcome",
      message: "Connected to ALBA Collector",
    })
  );
  console.log("[ALBA] WebSocket client connected");
});

// ---------------- START ----------------
server.listen(PORT, () => {
  console.log("[ALBA] Collector connected to Kloud backend");
  console.log(`   -> Listening on http://localhost:${PORT}`);
  console.log(`   -> Backend: ${BACKEND_API}`);
});

