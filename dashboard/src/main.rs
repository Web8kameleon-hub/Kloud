use actix_web::{web, App, HttpServer, Result};
use actix_files::Files;
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
struct NodeStatus {
    node_id: u64,
    tide_level: String,
    active_peers: usize,
    pq_keys_valid: bool,
}

async fn get_nodes() -> Result<web::Json<Vec<NodeStatus>>> {
    // Connect to PostgreSQL cluster view
    let nodes = vec![
        NodeStatus { node_id
