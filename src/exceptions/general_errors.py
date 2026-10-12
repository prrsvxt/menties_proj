class NotFoundError(Exception): ...


class InvalidTimezoneError(ValueError):
    def __init__(self) -> None:
        super().__init__('Некорректный часовой пояс')

class ConflictError(Exception): ...

