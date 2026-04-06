use crate::algebra::Op;
use crate::protocol::TideLevel;

pub struct PolicyDecision {
    pub allow_ops: Vec<Op>,
    pub gossip_interval_ms: u64,
    pub fanout: usize,
    pub allow_bulk: bool,
}

pub struct PolicyEngine;

impl PolicyEngine {
    pub fn decide(tide: TideLevel, load: f32) -> PolicyDecision {
        match tide {
            TideLevel::High => Self::high_policy(load),
            TideLevel::Normal => Self::normal_policy(load),
            TideLevel::Low => Self::low_policy(load),
        }
    }

    fn high_policy(_load: f32) -> PolicyDecision {
        PolicyDecision {
            allow_ops: vec![
                Op::S, Op::C, Op::R, Op::E,
                Op::P, Op::M, Op::F, Op::J,
                Op::L, Op::D, Op::T, Op::X,
            ],
            gossip_interval_ms: 500,
            fanout: 5,
            allow_bulk: true,
        }
    }

    fn normal_policy(_load: f32) -> PolicyDecision {
        PolicyDecision {
            allow_ops: vec![
                Op::S, Op::C, Op::R, Op::E,
                Op::P, Op::M, Op::F, Op::J,
                Op::D, Op::T,
            ],
            gossip_interval_ms: 1500,
            fanout: 3,
            allow_bulk: true,
        }
    }

    fn low_policy(_load: f32) -> PolicyDecision {
        PolicyDecision {
            allow_ops: vec![
                Op::S, Op::P, Op::M, Op::R,
            ],
            gossip_interval_ms: 3000,
            fanout: 2,
            allow_bulk: false,
        }
    }
}