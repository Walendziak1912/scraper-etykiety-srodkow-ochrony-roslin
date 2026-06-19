class AppError(Exception):
    default_message = "Wystąpił błąd aplikacji."
    error_code = "app_error"

    def __init__(self, message: str | None = None, **context: object) -> None:
        self.message = message or self.default_message
        self.context = context
        self.code = self.error_code
        super().__init__(self.message)
    
        if context:
            self.args = (self.message, context)
        else:
            self.args = (self.message,)

    def to_dict(self) -> dict[str, object]:
        return { 
            "ErrorCode": self.code,
            "Message": self.message,
            "Context": self.context,
        }
