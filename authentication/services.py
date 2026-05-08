import secrets
import time

import uuid
from accounts.models import User

import redis
from django.conf import settings

OTP_PURPOSE = ("login", "register")
OTP_TTL_SECONDS = 120
OTP_COOLDOWN_SECONDS = 120

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True # decode byte to str
)

def generate_otp_code() -> str:
    return str(secrets.randbelow(90000) + 10000)

# build_otp_key for redis
def build_otp_key(
        identifier: str,
        purpose: str
    ) -> str:
    if purpose not in OTP_PURPOSE:
        raise ValueError("Invalid OTP purpose.")
    return f"otp:{purpose}:{identifier}"

def build_otp_cooldown_key(identifier: str, purpose: str) -> str:
    if purpose not in OTP_PURPOSE:
        raise ValueError("Invalid OTP purpose.")
    return f"otp_cooldown:{purpose}:{identifier}"


def get_otp_cooldown_remaining(identifier: str, purpose: str) -> int:
    key = build_otp_cooldown_key(identifier, purpose)
    ttl = redis_client.ttl(key)

    if ttl == -2:
        return 0

    if ttl == -1:
        return OTP_COOLDOWN_SECONDS

    return ttl


def set_otp_cooldown(
    identifier: str,
    purpose: str,
    ttl: int = OTP_COOLDOWN_SECONDS,
) -> None:
    key = build_otp_cooldown_key(identifier, purpose)
    redis_client.setex(key, ttl, "1")

def store_otp(
        identifier: str,
        purpose: str,
        code: str,
        ttl: int = OTP_TTL_SECONDS,
    ):
    key = build_otp_key(identifier, purpose)

    redis_client.setex(key, ttl, code) # setex: set with expiration

def verify_otp(
        identifier: str,
        purpose: str,
        code: str
    ) -> bool:
    key = build_otp_key(identifier, purpose)
    stored_code = redis_client.get(key)

    if not stored_code:
        return False

    if stored_code != code:
        return False

    redis_client.delete(key)
    return True

def get_identifier_type(identifier:str) -> str:
    if "@" in identifier:
        return "email"
    return "phone"


def generate_temp_username() -> str:
    return f"user_{uuid.uuid4().hex[:10]}"
    
def get_user_by_identifier(identifier: str) -> User | None:
    identifier_type = get_identifier_type(identifier)

    if identifier_type == "email":
        return User.objects.filter(email=identifier).first()

    if identifier_type == "phone":
        return User.objects.filter(phone_number=identifier).first()

    raise ValueError("Invalid identifier type")


def user_exists_by_identifier(identifier: str) -> bool:
    return get_user_by_identifier(identifier) is not None


def create_user_by_identifier(identifier: str) -> User:
    identifier_type = get_identifier_type(identifier)

    if identifier_type == "email":
        return User.objects.create(
            email=identifier,
            username=generate_temp_username(),
            is_email_verified=True,
        )

    if identifier_type == "phone":
        return User.objects.create(
            phone_number=identifier,
            username=generate_temp_username(),
            is_phone_verified=True,
        )

    raise ValueError("Invalid identifier type")