use axum::{routing::get, Router};
use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/health", get(|| async { "edge_gateway: ok" }))
        .route("/route", get(|| async { "Edge routing active" }));

    let listener = TcpListener::bind("0.0.0.0:7000").await.unwrap();
    println!("edge_gateway running on 0.0.0.0:7000");
    axum::serve(listener, app).await.unwrap();
}
