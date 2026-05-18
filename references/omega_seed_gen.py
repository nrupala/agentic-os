import secrets
import hashlib

def generate_omega_master_seed():
    """Generates a 256-bit entropy seed for master key recovery."""
    # Generate 32 bytes of secure random entropy (256 bits)
    seed_entropy = secrets.token_bytes(32)
    master_seed = seed_entropy.hex()
    
    # Store a SHA-256 hash of the seed as a public 'Recovery ID' 
    # to verify the correct seed is entered later without exposing the seed itself.
    recovery_id = hashlib.sha256(seed_entropy).hexdigest()[:8]
    
    print("--- OMEGA MASTER RECOVERY SEED ---")
    print(f"RECOVERY ID: {recovery_id}")
    print(f"MASTER SEED: {master_seed}")
    print("----------------------------------")
    print("⚠️ WARNING: Write this down on a physical medium and store it in a safe.")
    print("If you lose this seed and your master.key file, YOUR DATA IS GONE.")

if __name__ == "__main__":
    generate_omega_master_seed()
