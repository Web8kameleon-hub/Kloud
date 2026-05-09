/**
 * Cloudflare Worker — Mesh Edge Node
 * Announces self to Kloud mesh every 10 minutes
 * Deploy to: kloud.com, aiagi.io, or any Cloudflare domain
 */

const KLOUD_MESH_API = "https://kloud.aiagi.io";
const ANNOUNCE_INTERVAL_MS = 10 * 60 * 1000; // 10 minutes

/**
 * Main request handler.
 * - /_mesh/announce triggers a manual announce
 * - everything else is passthrough
 */
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/_mesh/announce") {
      const result = await announceToMesh(env, url.hostname);
      return new Response(JSON.stringify(result), {
        status: 200,
        headers: { "content-type": "application/json; charset=utf-8" },
      });
    }

    return fetch(request);
  },

  async scheduled(event, env, ctx) {
    // Cron trigger: every 10 minutes via wrangler.toml
    ctx.waitUntil(announceToMesh(env, env.MESH_EDGE_HOST || "cloudflare-edge"));
  },
};

async function announceToMesh(env, hostname) {
  try {
    const meshApi = env.KLOUD_MESH_API || KLOUD_MESH_API;

    // Edge-node ID: stable numeric id based on hostname
    const edgeNodeId = hashToId(hostname);

    const apiAddr = `https://${hostname}`;

    // Gossip addr: n/a for Cloudflare (no inbound TCP sockets)
    const gossipAddr = "cloudflare-edge:0";

    const payload = {
      id: edgeNodeId,
      api_addr: apiAddr,
      gossip_addr: gossipAddr,
    };

    const resp = await fetch(`${meshApi}/peers/announce`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      throw new Error(`announce failed: ${resp.status} ${resp.statusText}`);
    }

    const data = await resp.json();
    return {
      ok: true,
      edge: hostname,
      announced: payload,
      mesh_response: data,
      at: new Date().toISOString(),
    };
  } catch (err) {
    return {
      ok: false,
      edge: hostname,
      error: err.message,
      at: new Date().toISOString(),
    };
  }
}

/**
 * Simple hash: hostname → stable numeric ID
 */
function hashToId(str) {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i);
  }
  return Math.abs(hash) % 1000000000;
}

