# Demo sample: RSA key generation (the scanner flags this comment as low confidence)
from Crypto.PublicKey import RSA
key = RSA.generate(2048)

# Symmetric encryption example
cipher_name = "AES-256-GCM"