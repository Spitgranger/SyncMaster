"""
Custom Exceptions defined with attributes to help with generating responses
"""

from datetime import datetime
from http import HTTPStatus


class HTTPError(Exception):
    """
    Base Class For HTTP Exceptions
    """

    http_code: HTTPStatus


class PermissionException(HTTPError):
    """
    Internal permission errors in the lambda
    """

    http_code = HTTPStatus.INTERNAL_SERVER_ERROR


class ExternalServiceException(HTTPError):
    """
    Errors relating to external services
    """

    http_code = HTTPStatus.INTERNAL_SERVER_ERROR


class ConditionCheckFailed(HTTPError):
    """
    Errors relating to a failing condition in dynamodb
    """

    http_code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, msg: str = "The provided condition was not met"):
        super().__init__(msg)


class ConditionValidationError(HTTPError):
    """
    Errors relating to a condition that is not valid by dynamodb constraints
    """

    http_code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, msg: str = "The provided condition does not meet dynamodb constraints"):
        super().__init__(msg)


class ResourceNotFound(HTTPError):
    """
    Error relating to a resource not being found
    """

    http_code = HTTPStatus.NOT_FOUND

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(f"Resource [{resource_id}] of type [{resource_type}] not found")


class ResourceConflict(HTTPError):
    """
    Error relating to a conflict in resources
    """

    http_code = HTTPStatus.CONFLICT

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(f"Resource [{resource_id}] of type [{resource_type}] already exists")


class ExitTimeConflict(HTTPError):
    """
    Error relating to an exit time already existing for a user's latest visit
    """

    http_code = HTTPStatus.CONFLICT

    def __init__(self, site_id: str, user_id: str):
        super().__init__(
            f"An exit is already logged at site [{site_id}] for user [{user_id}]'s latest visit"
        )


class TimeConsistencyException(HTTPError):
    """
    When attempting modifying a database entry, and a more recent request
    has already performed a modification
    """

    http_code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, key: str, timestamp: datetime):
        super().__init__(
            f"Action on [{key}] failed, item changed since request at [{timestamp.isoformat()}]"
        )
