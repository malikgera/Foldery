class IconAssignError(Exception):
    """Raised by a platform backend when an icon cannot be written or removed."""

    def __init__(self, message: str, *, code: str = "generic", **details: object):
        super().__init__(message)
        self.code = code
        self.details = details
