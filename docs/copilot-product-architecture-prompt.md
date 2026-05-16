# Copilot Prompt: Product Architecture Mode

Use this exact prompt in VS Code Copilot Chat when you want architecture-first behavior:

```text
Copilot, stop interpreting my project as a server admin or DevOps task.

This is a distributed Rust product with multiple backend services, not a single monolithic API.

I need you to focus ONLY on:
- Rust workspace structure
- multi-crate backend architecture
- service boundaries
- async Axum/Actix patterns
- systemd deployment
- edge gateway logic
- distributed fabric communication

Do NOT switch into "server setup mode".
Do NOT suggest Docker, Kubernetes, or cloud provisioning unless I explicitly ask.

You are assisting with PRODUCT ARCHITECTURE, not server administration.
```
