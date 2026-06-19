from .app_error import AppError

class ScrapyError(AppError):
    default_message = "Błąd warstwy scrapy."
    error_code = "scrapy_error"