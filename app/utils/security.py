import secrets
import uuid

from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_api_key() -> str:
    """Generate a new API key with the configured prefix."""
    return f"{settings.api_key_prefix}{secrets.token_hex(32)}"


def generate_claim_token() -> str:
    """Generate a claim token for agent ownership verification."""
    return f"katbook_claim_{uuid.uuid4()}"


def generate_verification_code() -> str:
    """Generate a human-readable verification code for Twitter verification."""
    words = ["alpha", "bravo", "delta", "echo", "foxtrot", "gamma", "hotel", "kilo"]
    word = secrets.choice(words)
    suffix = secrets.token_hex(2)
    return f"{word}-{suffix}"


def hash_api_key(api_key: str) -> str:
    """Bcrypt-hash the full API key for storage."""
    return pwd_context.hash(api_key)


def verify_api_key_hash(plain_key: str, hashed_key: str) -> bool:
    """Verify a plain API key against its stored bcrypt hash."""
    return pwd_context.verify(plain_key, hashed_key)


def get_api_key_prefix(api_key: str) -> str:
    """Extract the first 16 characters for fast indexed lookup."""
    return api_key[:16]
