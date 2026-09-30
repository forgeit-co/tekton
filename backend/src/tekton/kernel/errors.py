class DomainError(Exception):
    def __init__(self, code: str, params: dict[str, object]):
        super().__init__(code, params)
        self.code = code
        self.params = params
