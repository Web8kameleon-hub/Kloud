use reqwest::Client;
use serde::{Deserialize, Serialize};

pub struct SovereignAI {
    client: Client,
    ollama_url: String,
}

#[derive(Serialize)]
struct OllamaRequest {
    model: String,
    prompt: String,
    stream
