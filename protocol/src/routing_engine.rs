use algebra::TideLevel;

pub struct RoutingEngine;

impl RoutingEngine {
    pub fn select_peers(peers: &[crate::PeerInfo], tide: TideLevel, fanout: usize) -> Vec<crate::PeerInfo> {
        let mut scored: Vec<(f32, &crate::PeerInfo)> = peers.iter()
            .map(|p| (Self::score(p, tide), p))
            .collect();

        scored.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());

        scored.into_iter()
            .take(fanout)
            .map(|(_, p)| p.clone())
            .collect()
    }

    fn score(p: &crate::PeerInfo, tide: TideLevel) -> f32 {
        let base =
            (1.0 / (p.latency_ms as f32 + 1.0)) * 0.4 +
            (p.bandwidth_kbps as f32 / 10000.0) * 0.3 +
            (p.reliability * 0.2) -
            (p.load * 0.3);

        match tide {
            TideLevel::High => base,
            TideLevel::Normal => base * 0.8,
            TideLevel::Low => base * 0.5 - (p.latency_ms as f32 * 0.01),
        }
    }
}