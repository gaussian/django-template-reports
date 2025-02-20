class UnterminatedTagException(Exception):
    """Raised when a template tag starting with '{{' is not terminated by '}}' in the same paragraph."""

    pass


class UnresolvedTagError(Exception):
    """Raised when one or more template tags could not be resolved."""

    pass
