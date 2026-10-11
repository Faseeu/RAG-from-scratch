"""Safe exception messages never include credentials or provider response bodies."""


class JevError(RuntimeError):
    pass


class JevTransportError(JevError):
    pass


class JevResponseError(JevError):
    pass


class JevHTTPError(JevError):
    def __init__(self, status_code: int, retry_after: str | None = None):
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(f'Jev request failed with HTTP {status_code}')
