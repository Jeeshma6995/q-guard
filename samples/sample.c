from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519
from cryptography.hazmat.primitives.ciphers import algorithms
import hashlib

# Classical public-key cryptography
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
ecc_key = ec.generate_private_key(ec.SECP256R1())

# Classical signature algorithm
signature_key = ed25519.Ed25519PrivateKey.generate()

# Symmetric encryption and hashing
cipher = algorithms.AES(b'0' * 32)
digest = hashlib.sha256(b'hello').hexdigest()

# Quantum-safe algorithm examples (API names may vary by library)
# ML-KEM-768 for key establishment
# ML-DSA-65 for digital signatures