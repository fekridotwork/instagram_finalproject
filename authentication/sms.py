from django.conf import settings
from kavenegar import APIException, HTTPException, KavenegarAPI


def send_otp(identifier,purpose,code):
    if not settings.KAVENEGAR_API_KEY:
        print(f"[DEV OTP] {identifier}: {code}")
        return
    api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
    try:
        api.sms_send({
            "sender": settings.KAVENEGAR_SENDER,
            "receptor": identifier,
            "message": f"Your OTP code is {code}",
        })
    except (APIException, HTTPException) as error:
        raise RuntimeError(f"Kavenegar failed: {error}")