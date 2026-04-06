use std::net::{TcpListener, TcpStream};
use std::io::{Read, Write};
use crate::TideLevel;

#[derive(Clone, Debug)]
pub struct DynamicTidePolicy {
    pub normal_delay_ms: u64,
    pub allow_bulk_on_low_tide: bool,
}

impl Default for DynamicTidePolicy {
    fn default() -> Self {
        Self {
            normal_delay_ms: 50,
            allow_bulk_on_low_tide: false,
        }
    }
}

impl DynamicTidePolicy {
    pub fn from_env() -> Self {
        let mut policy = Self::default();

        if let Ok(delay) = std::env::var("NANOGRID_TIDE_NORMAL_DELAY_MS") {
            if let Ok(parsed) = delay.parse::<u64>() {
                policy.normal_delay_ms = parsed;
            }
        }

        if let Ok(allow_bulk) = std::env::var("NANOGRID_ALLOW_BULK_LOW_TIDE") {
            let normalized = allow_bulk.trim().to_ascii_lowercase();
            policy.allow_bulk_on_low_tide = matches!(normalized.as_str(), "1" | "true" | "yes" | "on");
        }

        policy
    }
}

pub struct TcpTransport {
    pub bind_addr: String,
}

impl TcpTransport {
    pub fn start_listener(&self, handler: impl Fn(Vec<u8>) + Send + 'static) {
        let listener = TcpListener::bind(&self.bind_addr).unwrap();

        std::thread::spawn(move || {
            for stream in listener.incoming() {
                if let Ok(mut s) = stream {
                    let mut buf = vec![0u8; 65536];
                    if let Ok(n) = s.read(&mut buf) {
                        handler(buf[..n].to_vec());
                    }
                }
            }
        });
    }

    pub fn send(&self, addr: &str, data: &[u8]) {
        if let Ok(mut stream) = TcpStream::connect(addr) {
            let _ = stream.write_all(data);
        }
    }
}

pub enum GossipFrame {
    Digest(Vec<u8>),
    Delta(Vec<u8>),
    Bulk(Vec<u8>),
}

impl TcpTransport {
    pub fn send_frame(&self, peer: &str, frame: GossipFrame) {
        let bytes = match frame {
            GossipFrame::Digest(d) => d,
            GossipFrame::Delta(d) => d,
            GossipFrame::Bulk(b) => b,
        };

        self.send(peer, &bytes);
    }

    pub fn tide_send(&self, peer: &str, frame: GossipFrame, tide: TideLevel) {
        let policy = DynamicTidePolicy::from_env();

        match tide {
            TideLevel::High => {
                // dërgo menjëherë
                self.send_frame(peer, frame);
            }
            TideLevel::Normal => {
                // dërgo me vonesë dinamike nga env
                std::thread::sleep(std::time::Duration::from_millis(policy.normal_delay_ms));
                self.send_frame(peer, frame);
            }
            TideLevel::Low => {
                // dërgo vetëm Digest/Delta, jo Bulk (nëse nuk lejohet nga policy dinamike)
                match frame {
                    GossipFrame::Bulk(_) if !policy.allow_bulk_on_low_tide => return,
                    _ => self.send_frame(peer, frame),
                }
            }
        }
    }
}