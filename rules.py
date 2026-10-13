"""Curated, explainable detection rules for common cryptographic API names.

These rules are heuristics, not proof that an algorithm is executed or vulnerable.
"""
RULES = [
    {
        "algorithm": "RSA",
        "patterns": [
            r"\bRSA\b",
            r"\bRSA_generate_key(?:_ex)?\b",
            r"\bKeyPairGenerator\.getInstance\s*\(\s*[\"']RSA[\"']",
            r"\b(?:rsa\.generate_private_key|RSA\.generate)\b",
        ],
        "family": "public-key",
        "default_purpose": "public-key cryptography (confirm key use)",
        "quantum_risk": "High",
        "recommendation": (
            "Confirm whether RSA is used for key establishment/encryption or signatures. "
            "For key establishment, assess a protocol using ML-KEM; for signatures, assess "
            "ML-DSA or SLH-DSA. These are migrations, not drop-in replacements."
        ),
    },
    {
        "algorithm": "ECDSA",
        "patterns": [
            r"\bECDSA\b",
            r"\bECDSA_sign\b",
            r"\bECDSA_do_sign\b",
            r"\bSignature\.getInstance\s*\(\s*[\"'](?:SHA\d+withECDSA|NONEwithECDSA)[\"']",
        ],
        "family": "public-key-signature",
        "default_purpose": "digital signature",
        "quantum_risk": "High",
        "recommendation": "Assess migration to ML-DSA or SLH-DSA for digital signatures.",
    },
    {
        "algorithm": "ECDH",
        "patterns": [
            r"\bECDH\b",
            r"\bKeyAgreement\.getInstance\s*\(\s*[\"']ECDH[\"']",
            r"\bEVP_PKEY_derive\b",
        ],
        "family": "key-establishment",
        "default_purpose": "key agreement (confirm curve and API context)",
        "quantum_risk": "High",
        "recommendation": "Assess migration to ML-KEM-based key establishment and a compatible protocol.",
    },
    {
        "algorithm": "Diffie-Hellman",
        "patterns": [
            r"\bDiffieHellman\b",
            r"\bDH_generate_key\b",
            r"\bDH_compute_key\b",
            r"\bKeyAgreement\.getInstance\s*\(\s*[\"']DH[\"']",
        ],
        "family": "key-establishment",
        "default_purpose": "key agreement",
        "quantum_risk": "High",
        "recommendation": "Assess migration to ML-KEM-based key establishment and a compatible protocol.",
    },
    {
        "algorithm": "AES",
        "patterns": [
            r"\bAES\b",
            r"\bAES_(?:encrypt|decrypt|set_encrypt_key|set_decrypt_key)\b",
            r"\bCipher\.getInstance\s*\(\s*[\"'][^\"']*AES[^\"']*[\"']",
        ],
        "family": "symmetric-encryption",
        "default_purpose": "symmetric encryption",
        "quantum_risk": "Context-dependent",
        "recommendation": (
            "AES is not broken by Shor's algorithm.Review key size, mode, nonce/IV handling "
            "and implementation. AES-256 is generally preferred when seeking a larger "
            "symmetric security margin against generic quantum search."
        ),
    },
    {
        "algorithm": "SHA-1",
        "patterns": [
            r"\bSHA1\b",
            r"\bSHA-1\b",
            r"\bMessageDigest\.getInstance\s*\(\s*[\"']SHA-?1[\"']",
        ],
        "family": "hash",
        "default_purpose": "hashing (confirm whether used for signatures, integrity, or legacy compatibility)",
        "quantum_risk": "Legacy / context-dependent",
        "recommendation": "Review the specific use and existing collision-resistance requirements; do not treat this as the same migration as RSA/ECC.",
    },
    {
        "algorithm": "SHA-256",
        "patterns": [
            r"\bSHA256\b",
            r"\bSHA-256\b",
            r"\bsha256\b",
            r"\bMessageDigest\.getInstance\s*\(\s*[\"']SHA-256[\"']",
        ],
        "family": "hash",
        "default_purpose": "hashing",
        "quantum_risk": "Generally retain; context-dependent",
        "recommendation": "Usually retain after reviewing the use case. Quantum effects differ from public-key attacks; do not automatically replace SHA-256.",
    },
    {
        "algorithm": "SHA-384/512",
        "patterns": [
            r"\bSHA(?:384|512)\b",
            r"\bSHA-?(?:384|512)\b",
            r"\bMessageDigest\.getInstance\s*\(\s*[\"']SHA-(?:384|512)[\"']",
        ],
        "family": "hash",
        "default_purpose": "hashing",
        "quantum_risk": "Generally retain; context-dependent",
        "recommendation": "Assess the application and security requirements; do not automatically replace a hash based only on its name.",
    },
]