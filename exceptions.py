class BadRequestError(Exception):
    """The server cannot or will not process the request due to an apparent client error"""


class ForbiddenError(Exception):
    """The request was valid, but the server is refusing action."""


class NotFoundError(Exception):
    """The requested resource could not be found but may be available in the future."""

