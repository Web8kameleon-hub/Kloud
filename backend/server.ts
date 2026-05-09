import express from "express";
import bodyParser from "body-parser";
import cors from "cors";
import http from "http";
import { loadConfig } from "./config";
import { initWebSocket } from "./layers/_shared/websocket";
import { initSignalCore } from "./layers/_shared/signal";
import { mountCore } from "./layers/layer1-core";
import { mountDdosSecurity } from "./layers/layer2-ddos";
import { mountMesh } from "./layers/layer3-mesh";
import { mountAlba } from "./layers/layer4-alba";
import { mountALBI } from "./layers/layer5-albi";
import { mountJONA } from "./layers/layer6-jona";
import { mountCuriosity } from "./layers/layer7-curiosity";
import { mountNeuroacoustic } from "./layers/layer8-neuroacoustic";
import { mountLayer9 } from "./layers/layer9-memory";
import { mountLayer10 } from "./layers/layer10-quantum";
import { mountLayer11 } from "./layers/layer11-agi";
import { mountLayer12 } from "./layers/layer12-asi";

async function bootstrap() {
  const cfg = loadConfig();
  const app = express();

  app.use(cors({ origin: cfg.CORS_ORIGIN ?? true, credentials: true }));
  app.use(bodyParser.json({ limit: "25mb" }));
  app.use(bodyParser.urlencoded({ extended: true, limit: "25mb" }));

  await initSignalCore({
    redisUrl: cfg.REDIS_URL,
    httpWebhook: cfg.SIGNAL_HTTP,
    secretKey: process.env.SIGNAL_SECRET ?? "Kloud-key",
  });

  // Layer 1 â€“ Core (health, logger, monitor)
  mountCore(app, cfg);

  // Layer 2 â€“ DDoS/EN Security (vendose sa mÃ« herÃ«t)
  mountDdosSecurity(app);

  // Layer 3 â€“ Mesh (LoRa/GSM/SAT)
  mountMesh(app, cfg);

  // Layer 4 â€“ ALBA (collector)
  mountAlba(app, cfg);

  // Layer 5 â€“ ALBI (EEG processing via Python MNE)
  mountALBI(app, cfg);

  // Layer 6 â€“ JONA (ethics + sandbox)
  mountJONA(app, cfg);

  // Layer 7 â€“ Curiosity Ocean
  mountCuriosity(app, cfg);

  // Layer 8 â€“ Neuroacoustic (EEGâ†’Audio)
  mountNeuroacoustic(app, cfg);

  // Layers 9-12 will be mounted after WebSocket initialization
  // to ensure proper real-time communication capabilities

  // HTTP server pÃ«r WebSocket
  const server = http.createServer(app);

  try {
    const wss = await initWebSocket(server, cfg.REDIS_URL);
    console.log("[System] WebSocket + Redis feed active");

    // Mount advanced layers with WebSocket support
    mountLayer9(app, wss);
    mountLayer10(app, wss);
    mountLayer11(app, wss);
    mountLayer12(app, wss);

    console.log("[System] All 12 layers mounted successfully");
  } catch (err) {
    console.error("[System] WS init error", err);
  }

  const port = cfg.PORT ?? 8000;
  server.listen(port, () => {
    console.log(`[API] up on ${port} (${cfg.NODE_ENV})`);
  });
}

void bootstrap().catch((err) => {
  console.error("[System] Bootstrap failed", err);
  process.exitCode = 1;
});

