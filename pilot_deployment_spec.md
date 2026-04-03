# Pilot Deployment Spec — 10 Nodes, Real-World Test

Nanogrid është një fabric i shpërndarë, sovereign, post-quantum secure dhe adaptive, i ndërtuar me Rust për performancë dhe siguri maksimale.

## 1. Objective

Deploy a minimal viable Sovereign Nanogrid Fabric with 10 nodes to validate gossip, algebra, PQC security, and offline tolerance in a controlled environment.

## 2. Topology

- Total Nodes: 10
- Locations: 3 edge sites (e.g., Berlin, Tokyo, Moscow)
- Distribution: 3–4 nodes per site
- Roles:
  - Core Nodes (7–8): Full storage, compute, gossip
  - Gateway Node (1): JSON API exposure
  - Observer Node (1): Read-only monitoring

## 3. Hardware

- Use RISC-V emulators or x86 for dev (target RISC-V production)
- Specs: As per Hᴜ spec (8 cores, 64GB RAM, NVMe storage)

## 4. Software Stack

- Rust runtime with Tokio
- CBOR2 for messages
- PQ crypto: Dilithium + Kyber
- Gossip: Tri-channel (digest, delta, bulk)
- Algebra: 12 ops with associativity/idempotence

## 5. Test Scenarios

- Gossip Latency: Measure message propagation time
- Offline/Online: Simulate node failures and reconnections
- PQC Overhead: CPU usage for signing/verifying
- Throughput: Ops/sec under load

## 6. Success Criteria

- Messages reach all active nodes in <2s average
- No state loss after partitions
- PQ crypto <30% CPU overhead
- Full restart without consistency loss

## 7. Deployment Steps

1. Provision VMs/containers at 3 sites
2. Install Rust + dependencies
3. Generate PQ keys per node
4. Start nodes with gossip mesh
5. Run automated tests
6. Monitor via observer node

This pilot proves the fabric's viability for global scale.
