import { NextResponse } from "next/server";

/**
 * SOVEREIGN FABRIC REGISTRY
 * -------------------------------------------------------------------------
 * Single source of truth for the proprietary fabric modules and their
 * routes / paths / aliases. No-fake policy: every entry carries an honest
 * evidence tag.
 *
 *   status:
 *     "live"     -> has a real backend endpoint reachable via alias
 *     "alias"    -> named path proxied to an existing backend
 *     "proposed" -> declared module, backend not yet implemented (measured=false)
 *
 *   measured:
 *     true  -> route resolves to a running backend service
 *     false -> declared / spec-only, not yet wired to telemetry
 *
 * Profile: wwwmmm-ndb-stigma-tide-rezonance-nanogrid
 */

type FabricStatus = "live" | "alias" | "proposed";

type FabricModule = {
  id: string;
  name: string;
  status: FabricStatus;
  measured: boolean;
  alias: string | null;
  backend: string | null;
  note: string;
};

const FABRIC_PROFILE = "wwwmmm-ndb-stigma-tide-rezonance-nanogrid";

const MODULES: FabricModule[] = [
  {
    id: "nanogrid",
    name: "Nanogrid Data",
    status: "live",
    measured: true,
    alias: "/api/nanogrid/status",
    backend: "nodedb-control-plane:9090 /api/v1/control-plane/nanogrid/status",
    note: "Signal grid status. Backend endpoint reachable (currently returns 500 - upstream nodedb issue).",
  },
  {
    id: "nanodecibel",
    name: "Nanodecibel",
    status: "proposed",
    measured: false,
    alias: "/api/nanodecibel",
    backend: null,
    note: "Sub-threshold acoustic measure. Spec-only; backend not yet wired.",
  },
  {
    id: "nodedb",
    name: "NodeDB",
    status: "live",
    measured: true,
    alias: "/api/nodedb",
    backend: "nodedb-control-plane:9090 /api/v1/control-plane/discovery",
    note: "Distributed state control plane.",
  },
  {
    id: "nodedb-fluid",
    name: "NodeDB Fluid",
    status: "live",
    measured: true,
    alias: "/api/nodedb-fluid",
    backend: "nodedb-control-plane:9090 /api/v1/control-plane/sync-loop/status",
    note: "Fluid replication / sync loop.",
  },
  {
    id: "stigma",
    name: "Stigma (BTI)",
    status: "live",
    measured: true,
    alias: "/api/stigma",
    backend: "nodedb-control-plane:9090 /api/v1/stigma/write",
    note: "Behavioral trace persistence.",
  },
  {
    id: "stigma-film-memory",
    name: "Stigma Film Memory",
    status: "live",
    measured: true,
    alias: "/api/stigma/events",
    backend: "nodedb-control-plane:9090 /api/v1/resonant/events",
    note: "Hash-chained event film (resonant chain).",
  },
  {
    id: "rezonance",
    name: "Rezonance",
    status: "live",
    measured: true,
    alias: "/api/rezonance",
    backend: "nodedb-control-plane:9090 /api/v1/resonant/events",
    note: "Resonant event fabric.",
  },
  {
    id: "tide",
    name: "Tide",
    status: "proposed",
    measured: false,
    alias: "/api/fabric-monitoring",
    backend: null,
    note: "Operational gating facet. No dedicated deployed endpoint yet; monitoring surfaced via /api/fabric-monitoring.",
  },
  {
    id: "scan-print",
    name: "Scanner-Thinker-Printer",
    status: "live",
    measured: true,
    alias: "/api/scan-print",
    backend: "nodedb-control-plane:9090 /api/v1/control-plane/scan-print",
    note: "Scan -> reason -> emit pipeline. Verified 200.",
  },
  {
    id: "wwwmmm",
    name: "WWWMMM",
    status: "proposed",
    measured: false,
    alias: null,
    backend: null,
    note: "Orchestration + quality gate profile. Runtime verdict endpoint not deployed yet.",
  },
  {
    id: "os-clx",
    name: "OS-CLX",
    status: "proposed",
    measured: false,
    alias: "/api/os-clx",
    backend: null,
    note: "System contract (docs/fabric-p0/OS_CLX.md). No runtime endpoint yet.",
  },
  {
    id: "cwy",
    name: "CWY",
    status: "proposed",
    measured: false,
    alias: "/api/cwy",
    backend: null,
    note: "Declared fabric facet. Backend not yet implemented.",
  },
  {
    id: "bridge",
    name: "Bridge",
    status: "proposed",
    measured: false,
    alias: "/api/bridge",
    backend: null,
    note: "Cycle-agent connector (internal class). No HTTP surface yet.",
  },
  {
    id: "zing",
    name: "Zing",
    status: "proposed",
    measured: false,
    alias: "/api/zing",
    backend: null,
    note: "Declared fabric facet. Backend not yet implemented.",
  },
  {
    id: "zero-noise",
    name: "Zero Noise",
    status: "proposed",
    measured: false,
    alias: "/api/zero-noise",
    backend: null,
    note: "Noise-floor gate. Spec-only; backend not yet wired.",
  },
  {
    id: "lighting",
    name: "Lighting",
    status: "proposed",
    measured: false,
    alias: "/api/lighting",
    backend: null,
    note: "Declared fabric facet. Backend not yet implemented.",
  },
  {
    id: "momentum",
    name: "Momentum",
    status: "proposed",
    measured: false,
    alias: "/api/momentum",
    backend: null,
    note: "Declared fabric facet. Backend not yet implemented.",
  },
  {
    id: "wave",
    name: "Wave",
    status: "live",
    measured: true,
    alias: "/api/jona",
    backend: "kloud-api:8000 /api/jona/* (brainwave synthesis)",
    note: "Waveform / brainwave synthesis.",
  },
];

export async function GET() {
  const live = MODULES.filter((m) => m.status === "live").length;
  const proposed = MODULES.filter((m) => m.status === "proposed").length;

  return NextResponse.json(
    {
      fabric_profile: FABRIC_PROFILE,
      policy: "no-fake: measured=true only when a running backend resolves the alias",
      totals: {
        modules: MODULES.length,
        live,
        proposed,
        measured: MODULES.filter((m) => m.measured).length,
      },
      modules: MODULES,
      generated_at: new Date().toISOString(),
    },
    {
      headers: { "Cache-Control": "no-store" },
    },
  );
}
