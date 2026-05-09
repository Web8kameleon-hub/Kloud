pub struct QuicTransport;

impl QuicTransport {
    pub async fn new(_bind_addr: &str) -> Result<Self, Box<dyn std::error::Error>> {
        Ok(QuicTransport)
    }

    pub async fn send(&self, _addr: &str, _data: Vec<u8>, _stream_id: u64) -> Result<(), Box<dyn std::error::Error>> {
        Ok(())
    }

    pub fn start_listener(&self, _handler: impl Fn(Vec<u8>, u64) + Send + Sync + 'static) {
        // QUIC transport is intentionally stubbed for portable builds.
    }
}