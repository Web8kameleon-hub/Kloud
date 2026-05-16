use axum::{routing::get, Router};
use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/health", get(|| async { "core_api: ok" }))
        .route("/api/v1/info", get(|| async { "Kloud Core API" }));

    let listener = TcpListener::bind("0.0.0.0:8000").await.unwrap();
    println!("core_api running on 0.0.0.0:8000");
    axum::serve(listener, app).await.unwrap();
}
