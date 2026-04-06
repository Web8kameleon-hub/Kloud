use super::algebra::{apply_ops, Op};
use super::TideLevel;

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

pub struct ExecutionPipeline;

impl ExecutionPipeline {
    pub fn execute(msg: &super::Message, policy: &PolicyDecision) -> Vec<u8> {
        let mut state = msg.payload.clone();

        for op_id in &msg.ops {
            if let Some(op) = Self::map_op(*op_id) {
                if !policy.allow_ops.contains(&op) {
                    continue; // op i bllokuar nga politika
                }

                state = Self::apply_single(op, &state);
            }
        }

        state
    }

    fn apply_single(op: Op, state: &[u8]) -> Vec<u8> {
        let ops = vec![op];
        apply_ops(&ops, state).state
    }

    fn map_op(id: u8) -> Option<Op> {
        match id {
            1 => Some(Op::S),
            2 => Some(Op::C),
            3 => Some(Op::R),
            4 => Some(Op::E),
            5 => Some(Op::P),
            6 => Some(Op::M),
            7 => Some(Op::F),
            8 => Some(Op::J),
            9 => Some(Op::L),
            10 => Some(Op::D),
            11 => Some(Op::T),
            12 => Some(Op::X),
            _ => None,
        }
    }
}