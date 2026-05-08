import secrets
import time

import uuid
from accounts.models import User

import redis
from django.conf import settings

OTP_PURPOSE = ("login", "register")
OTP_TTL_SECONDS = 120

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True # decode byte to str
)

def generate_otp_code() -> str:
    return str(secrets.randbelow(90000) + 10000)

# build_otp_key for redis
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
    ):
    key = build_otp_code(identifier, purpose)

    redis_client.setex(key, ttl, code) # setex: set with expiration

def verify_otp(
        identifier: str,
        purpose: str,
        code: str
    ) -> bool:
    key = build_otp_code(identifier, purpose)
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
def get_or_create_user_by_identifier(identifier:str) -> tuple[User, bool]:
    identifier_type = get_identifier_type(identifier)

    if identifier_type == "email":
        return User.objects.get_or_create(
            email=identifier,
            defaults={
                "username": generate_temp_username(),
            },
        )
    if identifier_type == "phone":
        return User.objects.get_or_create(
            phone_number=identifier,
            defaults={
                "username": generate_temp_username(),
            },
        )
    raise ValueError("Invalid identifier type")