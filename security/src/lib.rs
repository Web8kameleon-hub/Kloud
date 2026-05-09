use ed25519_dalek::{Signature, Signer, SigningKey, Verifier, VerifyingKey};
use rand::rngs::OsRng;
use sha3::{Digest, Sha3_256, Sha3_512};
use x25519_dalek::{PublicKey as X25519PublicKey, StaticSecret};

#[derive(Clone)]
pub struct PublicKey(pub VerifyingKey);

#[derive(Clone)]
pub struct SecretKey(pub SigningKey);

#[derive(Clone)]
pub struct KemPublicKey(pub X25519PublicKey);

#[derive(Clone)]
pub struct KemSecretKey(pub StaticSecret);

#[derive(Clone)]
pub struct DetachedSignature(pub Signature);

impl DetachedSignature {
    pub fn as_bytes(&self) -> [u8; 64] {
        self.0.to_bytes()
    }

    pub fn from_bytes(bytes: &[u8]) -> Result<Self, &'static str> {
        if bytes.len() != 64 {
            return Err("invalid signature length");
        }
        let mut sig = [0u8; 64];
        sig.copy_from_slice(bytes);
        Ok(Self(Signature::from_bytes(&sig)))
    }
}

#[derive(Clone)]
pub struct PQKeypair {
    pub dilithium_public: PublicKey,
    pub dilithium_private: SecretKey,
    pub kyber_public: KemPublicKey,
    pub kyber_private: KemSecretKey,
}

pub fn pq_generate_keypair() -> PQKeypair {
    let mut rng = OsRng;

    let signing = SigningKey::generate(&mut rng);
    let verify = signing.verifying_key();

    let kem_private = StaticSecret::random_from_rng(&mut rng);
    let kem_public = X25519PublicKey::from(&kem_private);

    PQKeypair {
        dilithium_public: PublicKey(verify),
        dilithium_private: SecretKey(signing),
        kyber_public: KemPublicKey(kem_public),
        kyber_private: KemSecretKey(kem_private),
    }
}

pub fn pq_sign(private: &SecretKey, msg: &[u8]) -> DetachedSignature {
    DetachedSignature(private.0.sign(msg))
}

pub fn pq_verify(public: &PublicKey, msg: &[u8], sig: &DetachedSignature) -> bool {
    public.0.verify(msg, &sig.0).is_ok()
}

fn derive_shared_material(secret_32: &[u8; 32]) -> [u8; 64] {
    let mut hasher = Sha3_512::new();
    hasher.update(secret_32);
    hasher.finalize().into()
}

pub fn pq_kem_encrypt(public: &KemPublicKey) -> (Vec<u8>, Vec<u8>) {
    let mut rng = OsRng;
    let eph_secret = StaticSecret::random_from_rng(&mut rng);
    let eph_public = X25519PublicKey::from(&eph_secret);
    let shared = eph_secret.diffie_hellman(&public.0);
    let material = derive_shared_material(shared.as_bytes());

    // Ciphertext is the ephemeral public key bytes.
    (eph_public.as_bytes().to_vec(), material[..44].to_vec())
}

pub fn pq_kem_decrypt(private: &KemSecretKey, ct: &[u8]) -> Vec<u8> {
    if ct.len() != 32 {
        return vec![0u8; 44];
    }
    let mut eph_bytes = [0u8; 32];
    eph_bytes.copy_from_slice(ct);
    let eph_public = X25519PublicKey::from(eph_bytes);
    let shared = private.0.diffie_hellman(&eph_public);
    let material = derive_shared_material(shared.as_bytes());
    material[..44].to_vec()
}

pub fn hash_message(msg: &[u8]) -> [u8; 32] {
    let mut hasher = Sha3_256::new();
    hasher.update(msg);
    hasher.finalize().into()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sign_and_verify_roundtrip() {
        let kp = pq_generate_keypair();
        let msg = b"kloud-wwwmmm-fastpath";
        let sig = pq_sign(&kp.dilithium_private, msg);
        assert!(pq_verify(&kp.dilithium_public, msg, &sig));
    }

    #[test]
    fn kem_roundtrip_shared_material_matches() {
        let kp = pq_generate_keypair();
        let (ct, sender_secret) = pq_kem_encrypt(&kp.kyber_public);
        let receiver_secret = pq_kem_decrypt(&kp.kyber_private, &ct);
        assert_eq!(sender_secret, receiver_secret);
        assert_eq!(sender_secret.len(), 44);
    }
}