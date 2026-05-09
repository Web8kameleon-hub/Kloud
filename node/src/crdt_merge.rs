use algebra::{apply_ops, Op};
use protocol::Message;
use sha3::{Sha3_256, Digest};

pub struct MergeEngine;

impl MergeEngine {
    pub fn merge(a: &Message, b: &Message) -> Message {
        // 1. Choose the "winner" by logical clock
        let winner = if a.clock >= b.clock { a } else { b };

        // 2. Combine ops (idempotent + associative)
        let mut ops = a.ops.clone();
        for op in &b.ops {
            if !ops.contains(op) {
                ops.push(*op);
            }
        }

        // 3. Merge payload via algebra
        let merged_payload = {
            let ops_a: Vec<Op> = a.ops.iter().filter_map(|o| Self::map_op(*o)).collect();
            let ops_b: Vec<Op> = b.ops.iter().filter_map(|o| Self::map_op(*o)).collect();

            let res_a = apply_ops(&ops_a, &a.payload);
            let res_b = apply_ops(&ops_b, &b.payload);

            // deterministic merge: hash-based tie breaker
            if Self::hash(&res_a.state) >= Self::hash(&res_b.state) {
                res_a.state
            } else {
                res_b.state
            }
        };

        // 4. Build merged message
        Message {
            ops,
            payload: merged_payload,
            ttl: winner.ttl,
            clock: winner.clock,
            sig: winner.sig.clone(),
            node_id: winner.node_id,
            flags: winner.flags,
        }
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

    fn hash(data: &[u8]) -> [u8; 32] {
        let mut h = Sha3_256::new();
        h.update(data);
        h.finalize().into()
    }
}