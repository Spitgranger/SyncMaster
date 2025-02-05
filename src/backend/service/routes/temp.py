"""
Temporary route for initial setup
"""

from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body
from aws_lambda_powertools.event_handler import Response, content_types
from typing_extensions import Annotated
from http import HTTPStatus

from ..environment import USER_POOL_CLIENT_ID, USER_POOL_ID
from ..models.user_authentication.user_request_response import (
    SigninRequest,
    SignupRequest,
    AdminSignupRequest,
)
from ..user_authentication.user_authentication import (
    AdminCognitoClient,
    CognitoClient,
    admin_create_user_handler,
    signin_user_handler,
    signup_user_handler,
)

from ..exceptions import (
    ForceChangePasswordException,
    ResourceNotFound,
    UnauthorizedException,
    ResourceNotFound,
)


router = Router()


@router.get("/test")
def thingy() -> dict:
    """
    Dummy route for use in initial project structure setup. Can be removed later.

    :return: dummy dict.
    """
    return {"Hello": "World"}


@router.post("/signup")
def signup_handler(body: Annotated[SignupRequest, Body()]):
    """
    Route to signup a new user
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    cognito_client = CognitoClient(USER_POOL_CLIENT_ID)
    return signup_user_handler(body, cognito_client)


@router.post("/create_user")
def create_user_handler(body: Annotated[AdminSignupRequest, Body()]):
    """
    Route to signup a new user
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    cognito_client = AdminCognitoClient(USER_POOL_CLIENT_ID, USER_POOL_ID)

    return admin_create_user_handler(body, cognito_client)


@router.post("/signin")
def signin_handler(body: Annotated[SigninRequest, Body()]):
    """
    Route to signup a new user
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    cognito_client = CognitoClient(USER_POOL_CLIENT_ID)
    return signin_user_handler(body, cognito_client)


@router.exception_handler(Exception)
def exception_handler(exception: Exception):
    """
    Exception handler for all exceptions generated on invocation of this router
    :param exception: The exception caught
    :return: Response containing the correct HTTP code and message of exception
    """
    if isinstance(exception, ForceChangePasswordException):
        return Response(
            status_code=exception.http_code.value,
            content_type=content_types.APPLICATION_JSON,
            body={"error": str(exception)},
        )

    return Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
        content_type=content_types.APPLICATION_JSON,
        body={"error": str(exception)},
    )
