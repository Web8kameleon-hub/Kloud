/**
 * Vercel Edge Function — Mesh Node
 * Announces to Kloud mesh every 10 minutes via cron/scheduler
 * Path: pages/api/mesh/announce.js or app/api/mesh/announce/route.js
 */

const KLOUD_MESH_API = "https://kloud.aiagi.io";

export const config = {
  runtime: "nodejs",
};

export default async function handler(req, res) {
  if (req.method === "GET") {
    // Manual announce
    const result = await announceToMesh(req);
    return res.status(200).json(result);
  }

  if (req.method === "POST") {
    // Scheduled announce (from external cron)
    const result = await announceToMesh(req);
    return res.status(200).json(result);
  }

  res.status(405).json({ error: "Method not allowed" });
}

async function announceToMesh(req) {
  try {
    const hostname = req.headers.host || "vercel-edge";
    const edgeNodeId = hashToId(hostname);

    const payload = {
      id: edgeNodeId,
      api_addr: `https://${hostname}/api/mesh/announce`,
      gossip_addr: "vercel-edge:0",
    };

    const resp = await fetch(`${KLOUD_MESH_API}/peers/announce`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      throw new Error(`${resp.status} ${resp.statusText}`);
    }

    const data = await resp.json();
    return {
      ok: true,
      announced: payload,
      response: data,
      timestamp: new Date().toISOString(),
    };
  } catch (err) {
    return {
      ok: false,
      error: err.message,
      timestamp: new Date().toISOString(),
    };
  }
}

function hashToId(str) {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i);
  }
  return Math.abs(hash) % 1000000000;
}

/**
 * CRON SETUP:
 * 
 * Use EasyCron or similar to call:
 *   GET https://yourdomain.vercel.app/api/mesh/announce
 * 
 * Every 10 minutes
 */
