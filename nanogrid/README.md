# Nanogrid: Sovereign PQ-Secure Adaptive Distributed Fabric

Nanogrid është një fabric i shpërndarë, sovereign, post-quantum secure dhe adaptive, i ndërtuar me Rust për performancë dhe siguri maksimale.

## Features

- **Post-Quantum Security**: Dilithium2 për signing, Kyber512 për KEM, AES-256-GCM për encryption.
- **Adaptive Behavior**: Tide Engine (High/Normal/Low) bazuar në metrics (peers, latency, bandwidth, load).
- **Tri-Channel Gossip**: Digest/Delta/Bulk për shpërndarje efikase.
- **CRDT Merge**: Deterministic merge për konsistencë pa konflikte.
- **Zero-Copy & Async**: Tokio, CBOR serialization, append-only storage.
- **API & Dashboard**: REST API dhe HTML dashboard për kontroll.
- **Real Metrics & Key Management**: Metrics nga transport, key store për PQ verify.
- **Performance Optimized**: Connection pooling, persistent TCP.

## Architecture

### Core Components

- **Algebra**: Σᴜ ops (S/C/R/E/P/M/F/J/L/D/T/X).
- **Security**: PQ primitives (sign/verify/KEM/encrypt).
- **Protocol**:
  - Transport: TCP/QUIC me connection pooling.
  - Memory Log: Append-only in-memory.
  - Execution Pipeline: Ops execution me policy.
  - Routing Engine: Peer selection inteligjent.
  - Storage Engine: Persistent, tide-aware, CRDT-friendly.
  - Replication Engine: Shpërndarje adaptive.
  - Merge-Sync Engine: Ribashkim pas partitions.
- **Node**: State machine, metrics, Tide compute, API.

### Tide Levels

- **High**: Aggressive (fast gossip, all ops, high replication).
- **Normal**: Balanced.
- **Low**: Conservative (slow, minimal ops, energy-saving).

## Installation

```bash
git clone <repo>
cd nanogrid
cargo build --release
```

## Usage

### Single Node

```bash
cargo run
```

### Multi-Node Test

```powershell
.\scripts\run_multi_node.ps1
```

### API Endpoints

- `POST /submit`: Submit ops (JSON: `{"ops":["S","C"], "payload":"base64_data"}`).
- `GET /status`: Node status (metrics, tide).
- `GET /peers`: Peer list.
- `GET /state`: Local state (key-value).
- `GET /dashboard`: HTML dashboard.

## Configuration

Përdor environment variables:

- `NODE_ID`: Node ID (default: 1).
- `LISTEN_PORT`: TCP listen port (default: 8080).
- `PEERS`: Comma-separated peer list (default: 2:8081,3:8082,4:8083,5:8084).

## Monitoring

- Prometheus: `prometheus.yml` për scraping nodes.
- Dashboard: Built-in HTML at `/dashboard`.

## Security

- Çdo mesazh është signed dhe encrypted me PQ.
- Key management për peer verification.
- Sovereign: Pa varësi nga central authorities.

## Performance

- Async Tokio me connection pooling.
- Real metrics nga transport (latency, bandwidth).
- Zero-copy CBOR, append-only logs.

## Roadmap

- PQ verify full activation.
- Grafana dashboard.
- QUIC transport.
- Global deployment specs.

Ky është fabric-i i gjeneratës së ardhshme – sovereign, adaptive, ultra-secure. 🚀

- **Deploy Global**: Spec-e për deployment prodhim.
- **Hardware Integration**: Integrim me RISC-V, node low-power.

Fabric-u është gati për prototip dhe zgjerim! 🌊

