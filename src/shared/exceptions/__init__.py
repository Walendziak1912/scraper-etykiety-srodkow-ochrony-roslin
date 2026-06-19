from .app_error import AppError
from .feature_errors import (
    CaptchaDetectionError,
    CookiePopupError,
    FeatureError,
    LoginFormError,
    TwoFactorVerificationError
)

__all__ = [
    "AppError"
]
