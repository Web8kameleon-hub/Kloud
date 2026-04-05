// main.rs — Ultra Nanogrid Fabric Entry Point

use tokio::sync::mpsc;
use crate::node::Node;

mod algebra;
mod gossip;
mod security;
mod node;

#[tokio::main]
async fn main() {
    let node_id: u64 = std::env::var("NODE_ID").unwrap_or("1".to_string()).parse().unwrap();
    let peers: Vec<u64> = vec![2, 3, 4, 5]; // Example peers

    // Channels for gossip
    let (digest_tx, digest_rx) = mpsc::channel(100);
    let (delta_tx, delta_rx) = mpsc::channel(100);
    let (bulk_tx, bulk_rx) = mpsc::channel(100);

    // Node inbox/outbox
    let (_inbox_tx, inbox_rx) = mpsc::channel(100);
    let (outbox_tx, _outbox_rx) = mpsc::channel(100);

    // Create Node
    let mut node = Node::new(
        node_id,
        peers,
        inbox_rx,
        outbox_tx,
        digest_tx,
        digest_rx,
        delta_tx,
        delta_rx,
        bulk_tx,
        bulk_rx,
    );

    // Run Node
    node.run().await;
}
