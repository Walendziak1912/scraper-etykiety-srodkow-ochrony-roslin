from .app_error import AppError

class FeatureError(AppError):
    default_message = "Błąd warstwy feature."
    error_code = "feature_error"

class CookiePopupError(FeatureError):
    default_message = "Błąd podczas obsługi popupu cookies."
    error_code = "cookie_popup_error"

class LoginFormError(FeatureError):
    default_message = "Błąd podczas obsługi formularza logowania."
    error_code = "login_form_error"

class TwoFactorVerificationError(FeatureError):
    default_message = "Błąd podczas obsługi weryfikacji dwuetapowej."
    error_code = "two_factor_verification_error"

class CaptchaDetectionError(FeatureError):
    default_message = "Błąd podczas detekcji CAPTCHA."
    error_code = "captcha_detection_error"
