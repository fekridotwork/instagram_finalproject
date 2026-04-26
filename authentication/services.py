import random
import time

OTP_PURPOSE = ("login", "register")
OTP_TTL_SECONDS = 120
_OTP_STORAGE = {}

def generate_otp_code() -> str:
    return str(random.randint(10000, 99999))

def build_otp_code(
        identifier: str,
        purpose: str
    ) -> str:
    if purpose not in OTP_PURPOSE:
        raise ValueError("Invalid OTP purpose.")
    return f"otp:{purpose}:{identifier}"

def store_otp(
        identifier: str,
        purpose: str,
        code: str,
        ttl: int = OTP_TTL_SECONDS,
    ) -> str:
    key = build_otp_code(identifier, purpose)
    expires_at = time.time() + OTP_TTL_SECONDS

    _OTP_STORAGE[key] = {
        "code": code,
        "expires_at": expires_at,
    }

def verify_otp(
        identifier: str,
        purpose: str,
        code: str
    ) -> bool:
    key = build_otp_code(identifier, purpose)
    otp_data = _OTP_STORAGE.get(key)

    if not otp_data:
        return False

    if time.time() > otp_data["expires_at"]:
        return False

    if otp_data["code"] != code:
        return False

    _OTP_STORAGE.pop(key, None)
    return True

def get_identifier_type(identifier:str) -> str:
    if "@" in identifier:
        return "email"
    return "phone"