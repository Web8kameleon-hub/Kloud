use sha3::{Digest, Sha3_256};
use pqcrypto::sign::dilithium2::*;
use pqcrypto::kem::kyber512::*;

pub struct PQKeypair {
    pub dilithium_public: PublicKey,
    pub dilithium_private: SecretKey,
    pub kyber_public: PublicKey,
    pub kyber_private: SecretKey,
}

pub fn pq_generate_keypair() -> PQKeypair {
    let (dilithium_pk, dilithium_sk) = keypair();
    let (kyber_pk, kyber_sk) = keypair();
    PQKeypair {
        dilithium_public: dilithium_pk,
        dilithium_private: dilithium_sk,
        kyber_public: kyber_pk,
        kyber_private: kyber_sk,
    }
}

pub fn pq_sign(private: &SecretKey, msg: &[u8]) -> DetachedSignature {
    detached_sign(msg, private)
}

pub fn pq_verify(public: &PublicKey, msg: &[u8], sig: &DetachedSignature) -> bool {
    verify_detached_signature(sig, msg, public).is_ok()
}

pub fn pq_kem_encrypt(public: &PublicKey) -> (Vec<u8>, Vec<u8>) {
    let (shared_secret, ciphertext) = encapsulate(public);
    (ciphertext.as_bytes().to_vec(), shared_secret.as_bytes().to_vec())
}

pub fn pq_kem_decrypt(private: &SecretKey, ct: &[u8]) -> Vec<u8> {
    let ciphertext = pqcrypto::kem::kyber512::Ciphertext::from_bytes(ct).unwrap();
    let shared_secret = decapsulate(&ciphertext, private);
    shared_secret.as_bytes().to_vec()
}

pub fn hash_message(msg: &[u8]) -> [u8; 32] {
    let mut hasher = Sha3_256::new();
    hasher.update(msg);
    hasher.finalize().into()
}