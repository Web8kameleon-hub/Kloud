use axum::{routing::get, Router};
use std::env;
use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/health", get(|| async { "core_api: ok" }))
        .route("/api/v1/info", get(|| async { "Kloud Core API" }));

    let bind_addr = env::var("CORE_API_BIND").unwrap_or_else(|_| "0.0.0.0:8000".to_string());
    let listener = TcpListener::bind(&bind_addr).await.unwrap();
    println!("core_api running on {}", bind_addr);
    axum::serve(listener, app).await.unwrap();
}
