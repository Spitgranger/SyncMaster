"""
Temporary route for initial setup
"""

from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.openapi.params import Body
from ..user_authentication.user_authentication import signup_user, signin_user
from typing_extensions import Annotated
from ..models.user_authentication.user_request_response import SignupRequest, SigninRequest

router = Router()


@router.get("/test")
def thingy() -> dict:
    """
    Dummy route for use in initial project structure setup. Can be removed later.

    :return: dummy dict.
    """
    return {"Hello": "World"}


@router.post("/signup")
def signup_handler(body: Annotated[SignupRequest, Body()]) -> dict:
    """
    Route to signup a new user

    :return: dictionary containing http response
    """
    return signup_user(body)


@router.post("/signin")
def signin_handler(body: Annotated[SigninRequest, Body()]) -> dict:
    """
    Route to signup a new user

    :return: dictionary containing http response
    """

    return signin_user(body)
