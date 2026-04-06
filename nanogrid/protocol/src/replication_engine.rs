use crate::routing_engine::RoutingEngine;
use crate::policy_engine::PolicyEngine;
use crate::{Message, TideLevel};
use crate::transport::GossipTransport;

pub struct ReplicationEngine;

impl ReplicationEngine {
    pub async fn replicate<T: GossipTransport>(
        msg: &Message,
        peers: &[crate::PeerInfo],
        tide: TideLevel,
        transport: &T,
    ) {
        // Get policy based on tide
        let policy = PolicyEngine::decide(tide, 0.0); // dummy load

        // 1. Zgjidh peers sipas routing engine
        let selected_peers = RoutingEngine::select_peers(peers, tide, policy.fanout);

        // 2. Përgatit payload
        let payload = crate::build_payload(vec![msg.clone()], 0, |_| vec![]); // TODO: clock and sign

        // 3. Dërgo në peers sipas tide
        for &peer_id in &selected_peers {
            let _ = transport.tide_send_payload(peer_id, &payload, tide).await;
        }
    }
}