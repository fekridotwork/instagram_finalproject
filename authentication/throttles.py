from rest_framework.throttling import ScopedRateThrottle


class OTPRateThrottle(ScopedRateThrottle):
    scope = "otp"