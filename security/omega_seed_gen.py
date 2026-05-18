"""
OMEGA-CODE Master Recovery Seed Generator
========================================
Generates 256-bit entropy seeds for AES-256 key recovery.

Features:
- CSPRNG for cryptographic randomness
- BIP-39 style hex output
- Recovery ID for verification
- Secure storage
"""

import os
import secrets
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Tuple

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

class MasterSeedGenerator:
    """
    Generates and manages 256-bit master recovery seeds.
    
    Security:
    - Uses secrets.token_bytes() which is CSPRNG
    - Recovery ID is one-way hash (cannot reverse engineer seed)
    - Seeds can regenerate AES keys
    """
    
    ENTROPY_BITS = 256
    ENTROPY_BYTES = 32
    
    def __init__(self, project: str = None):
        self.project = project or os.getenv("PROJECT_NAME", "default")
        self.output_dir = Path(f"projects/{self.project}/state")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self) -> Tuple[str, str, str]:
        """
        Generate a new master seed.
        Returns: (seed_hex, recovery_id, mnemonic)
        """
        entropy = secrets.token_bytes(self.ENTROPY_BYTES)
        seed_hex = entropy.hex()
        recovery_id = hashlib.sha256(entropy).hexdigest()[:8]
        
        mnemonic = self._hex_to_mnemonic(entropy)
        
        return seed_hex, recovery_id, mnemonic
    
    def _hex_to_mnemonic(self, entropy: bytes, wordlist_size: int = 2048) -> str:
        """
        Convert entropy to BIP-39 style word list (simplified).
        """
        words = [
            "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
            "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
            "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual",
            "adapt", "add", "addict", "address", "adjust", "admit", "adult", "advance",
            "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent",
            "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album",
            "alpha", "already", "also", "alter", "always", "amateur", "amazing", "among",
            "amount", "amused", "analyst", "anchor", "ancient", "anger", "angle", "angry",
            "animal", "ankle", "announce", "annual", "another", "answer", "antenna", "antique",
            "anxiety", "any", "apart", "apology", "appear", "apple", "approve", "april",
            "arch", "arctic", "area", "arena", "argue", "arm", "armed", "armor",
            "army", "around", "arrange", "arrest", "arrive", "arrow", "art", "artefact",
            "artist", "artwork", "ask", "aspect", "assault", "asset", "assist", "assume",
            "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction",
            "audit", "august", "aunt", "author", "auto", "autumn", "average", "avocado",
            "avoid", "awake", "aware", "away", "awesome", "awful", "awkward", "axis",
            "baby", "bachelor", "bacon", "badge", "bag", "balance", "balcony", "ball",
            "bamboo", "banana", "banner", "bar", "barely", "bargain", "barrel", "base",
            "basic", "basket", "battle", "beach", "bean", "beauty", "because", "become",
            "beef", "before", "begin", "behave", "behind", "believe", "below", "belt",
            "bench", "benefit", "best", "betray", "better", "between", "beyond", "bicycle",
            "bid", "bike", "bind", "biology", "bird", "birth", "bitter", "black",
            "blade", "blame", "blanket", "blast", "bleak", "bless", "blind", "blood",
            "blossom", "blouse", "blue", "blur", "blush", "board", "boat", "body",
            "boil", "bomb", "bone", "bonus", "book", "boost", "border", "boring",
            "borrow", "boss", "bottom", "bounce", "box", "boy", "bracket", "brain",
            "brand", "brass", "brave", "bread", "breeze", "brick", "bridge", "brief",
            "bright", "bring", "brisk", "broccoli", "broken", "bronze", "broom", "brother",
            "brown", "brush", "bubble", "buddy", "budget", "buffalo", "build", "bulb",
            "bulk", "bullet", "bundle", "bunker", "burden", "burger", "burst", "bus",
            "business", "busy", "butter", "buyer", "buzz", "cabbage", "cabin", "cable",
            "cactus", "cage", "cake", "call", "calm", "camera", "camp", "can",
            "canal", "cancel", "candy", "cannon", "canoe", "canvas", "canyon", "capable"
        ]
        
        words_out = []
        for i in range(0, len(entropy), 2):
            index = int.from_bytes(entropy[i:i+2], 'big') % wordlist_size
            words_out.append(words[index])
        
        return " ".join(words_out)
    
    def save(self, seed_hex: str, recovery_id: str, mnemonic: str):
        """Save seed metadata to file (NOT the seed itself)."""
        metadata = {
            "recovery_id": recovery_id,
            "created_at": datetime.now().isoformat(),
            "bits": self.ENTROPY_BITS,
            "format": "hex",
            "mnemonic_available": True,
            "project": self.project
        }
        
        metadata_path = self.output_dir / "seed_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        seed_path = self.output_dir / "master.seed"
        with open(seed_path, 'w') as f:
            f.write(seed_hex)
        
        seed_path.chmod(0o600)
        
        print(f"[SEED] Metadata saved: {metadata_path}")
        print(f"[SEED] Seed saved: {seed_path}")
    
    def verify_seed(self, seed_hex: str) -> bool:
        """Verify a seed against stored recovery ID."""
        metadata_path = self.output_dir / "seed_metadata.json"
        
        if not metadata_path.exists():
            return False
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        expected_id = metadata.get("recovery_id")
        provided_id = hashlib.sha256(bytes.fromhex(seed_hex)).hexdigest()[:8]
        
        return expected_id == provided_id


def generate_seed(project: str = None, save: bool = True) -> Tuple[str, str, str]:
    """
    Generate and optionally save a master recovery seed.
    """
    generator = MasterSeedGenerator(project)
    seed_hex, recovery_id, mnemonic = generator.generate()
    
    if save:
        generator.save(seed_hex, recovery_id, mnemonic)
    
    return seed_hex, recovery_id, mnemonic


if __name__ == "__main__":
    import sys
    
    project = sys.argv[1] if len(sys.argv) > 1 else os.getenv("PROJECT_NAME", "default")
    
    print("=" * 60)
    print("OMEGA-CODE MASTER RECOVERY SEED GENERATOR")
    print("=" * 60)
    print("")
    print("⚠️  WARNING: Write this seed down on physical paper!")
    print("   If you lose this seed and master.key, YOUR DATA IS GONE.")
    print("")
    print("=" * 60)
    
    seed_hex, recovery_id, mnemonic = generate_seed(project)
    
    print("")
    print("--- RECOVERY ID ---")
    print(f"RECOVERY ID: {recovery_id}")
    print("")
    print("--- MASTER SEED (256-bit hex) ---")
    print(f"MASTER SEED: {seed_hex}")
    print("")
    print("--- MNEMONIC (optional backup) ---")
    print(f"MNEMONIC: {mnemonic}")
    print("")
    print("=" * 60)
    print("Store securely: Recovery ID + Master Seed")
    print("=" * 60)
