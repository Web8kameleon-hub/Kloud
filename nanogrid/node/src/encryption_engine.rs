use crate::security::{pq_kem_encrypt, pq_kem_decrypt};
use aes_gcm::{Aes256Gcm, Key, Nonce};
use aes_gcm::aead::{Aead, NewAead};

pub struct EncryptionEngine;

impl EncryptionEngine {
    pub fn encrypt(public_key: &pqcrypto::kem::kyber512::PublicKey, payload: &[u8]) -> (Vec<u8>, Vec<u8>) {
        // 1. Kyber KEM → shared secret
        let (ciphertext, shared_secret) = pq_kem_encrypt(public_key);

        // 2. AES-256-GCM me shared secret
        let key = Key::from_slice(&shared_secret[..32]);
        let cipher = Aes256Gcm::new(key);

        let nonce = Nonce::from_slice(&shared_secret[32..44]); // 12 bytes
        let encrypted = cipher.encrypt(nonce, payload).unwrap();

        (ciphertext, encrypted)
    }

    pub fn decrypt(private_key: &pqcrypto::kem::kyber512::SecretKey, ciphertext: &[u8], encrypted: &[u8]) -> Vec<u8> {
        // 1. Kyber decrypt → shared secret
        let shared_secret = pq_kem_decrypt(private_key, ciphertext);

        // 2. AES-256-GCM decrypt
        let key = Key::from_slice(&shared_secret[..32]);
        let cipher = Aes256Gcm::new(key);

        let nonce = Nonce::from_slice(&shared_secret[32..44]);
        cipher.decrypt(nonce, encrypted).unwrap()
    }
}