class UnterminatedTagException(Exception):
    """Raised when a template tag starting with '{{' is not terminated by '}}' in the same paragraph."""

    pass


class PermissionDeniedException(Exception):
    """Raised when one or more expressions fail the permission check."""

    def __init__(self, errors):
        self.errors = errors
        msg = "Permission denied for the following expressions: " + ", ".join(errors)
        super().__init__(msg)


class UnresolvedTagError(Exception):
    """Raised when one or more template tags could not be resolved."""

    pass
