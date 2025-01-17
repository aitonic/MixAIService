import hashlib
import uuid
from datetime import datetime

"""
    Unique ID generator
"""


def generate_by_sha256(seed_string: str = None) -> str:
    """Generate 64-bit result using SHA256 hash algorithm
    
    Args:
        seed_string (str, optional): Seed string for hash generation. Defaults to None.
    
    Returns:
        str: 64-character hexadecimal hash string

    """
    if not seed_string or len(seed_string) == 0:
        # Use current timestamp as seed if seed is empty
        seed_string = str(datetime.now().timestamp())
    sha_signature = hashlib.sha256(seed_string.encode()).hexdigest()
    return sha_signature


def generate_by_uuid(name: str = None) -> str:
    """Generate unique ID using UUID
    
    Args:
        name (str, optional): Name for UUID generation. Defaults to None.
    
    Returns:
        str: UUID string without hyphens

    """
    if not name or len(name) == 0:
        # Use random UUID if name is empty
        return uuid.uuid4().__str__().replace("-", "")
    # Generate UUID5
    return uuid.uuid5(uuid.NAMESPACE_X500, name).__str__().replace("-", "")
