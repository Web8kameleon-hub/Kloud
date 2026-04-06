use quinn::{Endpoint, ClientConfig, ServerConfig, Connection};
use std::sync::Arc;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

pub struct QuicTransport {
    pub endpoint: Endpoint,
}

impl QuicTransport {
    pub async fn new(bind_addr: &str) -> Result<Self, Box<dyn std::error::Error>> {
        // Placeholder certificates - in production, use proper certs
let cert = rcgen::generate_simple_self_signed(vec!["localhost".into()])?;
        let key_der = cert.serialize_private_key_der();
        let cert_der = cert.serialize_der()?;
        
        let cert_chain = vec![rustls::Certificate(cert_der)];
        let priv_key = rustls::PrivateKey(key_der);
        let mut crypto = rustls::ServerConfig::builder()
            .with_safe_defaults()
            .with_no_client_auth()
            .with_single_cert(cert_chain, priv_key)
            .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidInput, e))?;
        let server_config = ServerConfig::with_crypto(Arc::new(crypto));
        let mut endpoint = Endpoint::server(server_config, bind_addr.parse()?)?;

        Ok(QuicTransport { endpoint })
    }

    pub async fn send(&self, addr: &str, data: Vec<u8>, stream_id: u64) -> Result<(), Box<dyn std::error::Error>> {
        let conn = self.endpoint.connect(addr.parse()?, "nanogrid")?.await?;
        let mut stream = conn.open_uni().await?;
        stream.write_all(&data).await?;
        stream.finish().await?;
        Ok(())
    }

    pub fn start_listener(&self, handler: impl Fn(Vec<u8>, u64) + Send + Sync + 'static) {
        let endpoint = self.endpoint.clone();

        tokio::spawn(async move {
            while let Some(conn) = endpoint.accept().await {
                let handler = Arc::new(handler);

                tokio::spawn(async move {
                    let conn = conn.await.unwrap();

                    while let Ok(Some(mut stream)) = conn.accept_uni().await {
                        let mut buf = Vec::new();
                        stream.read_to_end(64 * 1024, &mut buf).await.unwrap();

                        let stream_id = stream.id().index();
                        handler(buf, stream_id);
                    }
                });
            }
        });
    }
}