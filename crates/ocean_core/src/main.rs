use axum::{routing::get, Router};
use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/health", get(|| async { "ocean_core: ok" }))
        .route("/fabric/state", get(|| async { "Ocean Core Fabric State" }));

    let listener = TcpListener::bind("0.0.0.0:9000").await.unwrap();
    println!("ocean_core running on 0.0.0.0:9000");
    axum::serve(listener, app).await.unwrap();
}
