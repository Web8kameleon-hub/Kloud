# Build stage
FROM rust:1.72 AS builder
WORKDIR /usr/src/ultra-fabric

COPY Cargo.toml Cargo.lock ./
COPY src ./src
COPY nanogrid ./nanogrid

RUN cargo build --release

# Runtime stage
FROM debian:bullseye-slim
WORKDIR /app
COPY --from=builder /usr/src/ultra-fabric/target/release/ultra-nanogrid-fabric .
CMD ["./ultra-nanogrid-fabric"]