"""
Temporary route for initial setup
"""

from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body
from typing_extensions import Annotated

from ..environment import USER_POOL_CLIENT_ID
from ..models.user_authentication.user_request_response import SigninRequest, SignupRequest
from ..user_authentication.user_authentication import (
    CognitoClient,
    signin_user_handler,
    signup_user_handler,
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


@router.post("/signin")
def signin_handler(body: Annotated[SigninRequest, Body()]):
    """
    Route to signup a new user
    :param body: The body of the HTTP request
    :return: dictionary containing http response
    """
    cognito_client = CognitoClient(USER_POOL_CLIENT_ID)
    return signin_user_handler(body, cognito_client)
