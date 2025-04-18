from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError

ph = PasswordHasher()

def hash_password(password: str):
    return ph.hash(password=password)

def verify_hash(hashed_password: str, password: str):
    try:
        return ph.verify(hash=hashed_password, password=password)
    except VerifyMismatchError:
        return False
def check_needs_rehash(hashed_password: str):
    return ph.check_needs_rehash(hash=hashed_password)