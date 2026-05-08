from celery import shared_task

from .sms import send_otp

@shared_task
def send_otp_task(identifier, purpose, code):
    send_otp(identifier, purpose, code)